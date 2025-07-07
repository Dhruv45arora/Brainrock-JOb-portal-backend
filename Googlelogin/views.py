from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from google.oauth2 import id_token
from django.conf import settings
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from .models import CustomUser
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import PostedJob
from rest_framework.generics import CreateAPIView
from .serializers import PostedJobSerializer,SavedpostbyuserSerializer
from .models import Save_post_By_user
from .models import Plan1, FinalSubscriptionForEmployee
from .serializers import Plan1Serializer, FinalSubscriptionForEmployeeSerializer
from django.shortcuts import get_object_or_404
User = get_user_model()

class Savedpost(CreateAPIView):
    queryset = Save_post_By_user.objects.all()
    serializer_class = SavedpostbyuserSerializer



class SavedPostsByUserView(APIView):
    def get(self, request, user_id):
        saved_posts = Save_post_By_user.objects.filter(user_id=user_id)
        if not saved_posts.exists():
            return Response({"message": "No saved posts found for this user"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SavedpostbyuserSerializer(saved_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class DeltePostByUserView(APIView):
    def delete(self, request, job_id):
        try:
            saved_post = Save_post_By_user.objects.get(job_id=job_id)
            saved_post.delete()
            return Response({'message': 'Saved post deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Save_post_By_user.DoesNotExist:
            return Response({'error': 'Saved post not found'}, status=status.HTTP_404_NOT_FOUND)

    
class PostedJobListCreateView(CreateAPIView):
    queryset = PostedJob.objects.all().order_by('-date')
    serializer_class = PostedJobSerializer

    def perform_create(self, serializer):
        employee_id = self.request.data.get("employee_id")

        if not employee_id:
            raise ValidationError({"error": "employee_id is required"})

        # Count how many jobs this employee already posted
        job_count = PostedJob.objects.filter(employee_id=employee_id).count()

        # Get subscription and plan
        try:
            subscription = FinalSubscriptionForEmployee.objects.get(employee_id=employee_id)
            plan = Plan1.objects.get(plan_id=subscription.plan_id)
            allowed_post_limit = plan.post
        except FinalSubscriptionForEmployee.DoesNotExist:
            raise ValidationError({"error": "No subscription found for this employee"})
        except Plan1.DoesNotExist:
            raise ValidationError({"error": "Plan not found for this employee"})

        # Restrict if limit exceeded
        if job_count >= allowed_post_limit:
            raise ValidationError({"error": f"Post limit reached: {allowed_post_limit} allowed"})

        # Save the job if within limit
        serializer.save()
    
    

class PostedJobDetailView(RetrieveUpdateDestroyAPIView):
    queryset = PostedJob.objects.all()
    serializer_class = PostedJobSerializer

class JobTitleSuggestionView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if query:
            jobs = PostedJob.objects.filter(job_title__icontains=query).values_list('job_title', flat=True).distinct()[:10]
            return Response(jobs)
        return Response([], status=status.HTTP_200_OK)

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("token")
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            refresh=RefreshToken.for_user(User)

            return Response({
                'user': {
                    'email': idinfo.get('email'),
                    'name': f"{idinfo.get('given_name')} {idinfo.get('family_name')}",
                    'picture': idinfo.get('picture'),
                    'locale': idinfo.get('locale'),
                    'email_verified': idinfo.get('email_verified'),
                    'sub': idinfo.get('sub'),
                    'given_name': idinfo.get('given_name'),
                    'family_name': idinfo.get('family_name'),
                    'access':str(refresh.access_token),
                    'refresh':str(refresh),
                }
            })

        except Exception as e:
            return Response({'error': 'Token Invalid', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CustomUserView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            
            refresh=RefreshToken.for_user(user)
            
            return Response({
                "message": "User created successfully",
                "access":str(refresh.access_token),
                "refresh":str(refresh),
                "id": user.id,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Getview(APIView):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not password:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            user = None
            if phone:
                user = get_object_or_404(CustomUser,phone=phone)
            elif email:
                user = get_object_or_404(CustomUser,email=email)
            else:
                return Response({"error": "Phone or Email is required"}, status=status.HTTP_400_BAD_REQUEST)

           
            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": user.name
            })

        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateView(APIView):
    parser_classes=[MultiPartParser,FormParser]
    def put(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       
        
        


# ---- Plan1 ----
class PlanListCreateView(APIView):
    def get(self, request):
        plans = Plan1.objects.all()
        serializer = Plan1Serializer(plans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = Plan1Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanDetailView(APIView):
    def get(self, request, plan_id):
        plan = get_object_or_404(Plan1, plan_id=plan_id)
        serializer = Plan1Serializer(plan)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self, request,plan_id):
        plan = get_object_or_404(Plan1,plan_id=plan_id)
        serializer = Plan1Serializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,plan_id):
        plan = get_object_or_404(Plan1,plan_id=plan_id)
        plan.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---- FinalSubscriptionForEmployee ----
class SubscriptionListCreateView(APIView):
    def get(self, request):
        plan = FinalSubscriptionForEmployee.objects.all()
        serializer = FinalSubscriptionForEmployeeSerializer(plan,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FinalSubscriptionForEmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionDetailView(APIView):
    def get(self, request,employee_id):
        employee = get_object_or_404(FinalSubscriptionForEmployee, employee_id=employee_id)
        plan=get_object_or_404(Plan1, plan_id=employee.plan_id)
        plan_serializer = Plan1Serializer(plan)
        total_post=plan.post
        print("Total post:",total_post)
        return Response(plan_serializer.data,status=status.HTTP_200_OK)
