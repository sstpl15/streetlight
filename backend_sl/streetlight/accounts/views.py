from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.contrib.sessions.backends.db import SessionStore
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout 
from django.utils.decorators import method_decorator
from datetime import datetime
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse

 
class UserCreate(APIView):
    def post(self, request, format='json'):
        if request.method == 'POST':
            data = request.data.copy()  # Create a mutable copy of the QueryDict
            print(data, 'RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR')
            print(data['role'], 'ggggggggggggggggggggggggggggggggggg')

            if data['role'] == "superadmin":
                data['is_superuser'] = True
                data['is_staff'] = False

            elif data['role'] == 'staff':
                data['is_superuser'] = False
                data['is_staff'] = True

            else:
                data['is_superuser'] = False
                data['is_staff'] = False

            serializer = UserSerializer(data=data)  # Use the modified data

            if serializer.is_valid():
                user = serializer.save()
                if user:
                    token = Token.objects.create(user=user)
                    json = serializer.data
                    json['token'] = token.key
                    return Response(json, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     

@api_view(['POST'])
def loginAPI(request):
    if request.method == "POST":
        obj = request.data
        user_email = obj['email']
        password = obj['password']
        print(user_email)
        print(password)

        try:
            user = CustomUser.objects.get(email=user_email)
            print(user, 'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV')
        except CustomUser.DoesNotExist:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        if check_password(password, user.password):
            login(request, user)
            print('yessssss')

            # Create session
            session = SessionStore()
            session['user_id'] = user.id
            session.save()

            # Generate token
            token = session.session_key
            users = CustomUser.objects.filter(email=user_email).values()
            user_name=users[0]['username']
            print(user_name,'user_nameuser_nameuser_nameuser_name')

            print(users, 'ggggggggggggggggggggggggggggggggggg')
            if users[0]['role'] == 'admin':
                print('OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
                roles = CustomUser.objects.filter(email=user_email).values()
                all_users_list=CustomUser.objects.all().values()
                serializer = UserSerializer(roles, many=True)
                data = serializer.data
                print(data)
                context={
                'data':data,
                'all_users_list':all_users_list,
                'token':token
                }
                return Response(context)

            elif users[0]['role'] == 'superadmin':
                print('OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
                roles = CustomUser.objects.filter(email=user_email).values()
                all_users_list=CustomUser.objects.all().values()
                serializer = UserSerializer(roles, many=True)
                data = serializer.data
                 
                context={
                'data':data,
                'all_users_list':all_users_list,
                'token':token
                }
                return Response(context)

            elif users[0]['role'] == 'staff':
                # Fetch the staff user object
                user_obj = CustomUser.objects.get(email=user_email)
                all_users_list=CustomUser.objects.filter(login_user_name=user_name).values()

                # Serialize the staff user object using the UserSerializer
                serializer = UserSerializer(user_obj)

                data = serializer.data
                 
                context={
                'data':data,
                'all_users_list':all_users_list,
                'token':token
                }
                return Response(context)
 

            elif users[0]['role'] == 'user':
                # Fetch the regular user object
                user_obj = CustomUser.objects.get(email=user_email)

                all_users_list=CustomUser.objects.filter(login_user_name=user_name).values()

                # Serialize the staff user object using the UserSerializer
                serializer = UserSerializer(user_obj)

                data = serializer.data
                 
                context={
                'data':data,
                'all_users_list':all_users_list,
                'token':token
                }
                return Response(context)

                

            else:
                # Handle unrecognized role
                return Response({'message': 'Unrecognized role'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def logoutapi(request):
    if request.method == 'POST':
        user_email = request.data.get('email')  # Retrieve email from request data
        print(user_email)  # Get the email from the request

        try:
            user = CustomUser.objects.get(email=user_email)
            print(user)
            logout(request)
            return Response({'message': 'Logged out successfully'})
        except ObjectDoesNotExist:
            print('User not found')
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method Not Allowed '}, status=status.HTTP_400_BAD_REQUEST)




 


@api_view(['GET'])
def delete_user(request,email):
    if request.method == 'GET':
        user_email = email   # Get the email from the request

        user = get_object_or_404(CustomUser, email=user_email)  # Get the user object based on the email
        user.delete()
        return Response('Success', status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST) # Delete the user

    # Handle your response or redirect as needed
 
# @api_view(['POST'])
# def update_user(request):
#     if request.method == 'POST':
#         user_email = request.POST.get('user_email')  # Get the email from the request

#         user = get_object_or_404(CustomUser, email=user_email)  # Get the user object based on the email

#         # Get updated values from the request
#         updated_username = request.POST.get('updated_username')
#         updated_email = request.POST.get('updated_email')

#         # Update user data
#         user.username = updated_username
#         user.email = updated_email
#         user.save()
#         return Response('Success', status=status.HTTP_200_OK)
#     else:
#         return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateAPIView(APIView):
    def patch(self, request):
        user_email = request.data.get('email')  # Get the email from the request data

        user = get_object_or_404(CustomUser, email=user_email)  # Get the user object based on the email

        # Deserialize the user data from the request data
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response('Success', status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 


def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def custom_password_change_view(request):
    # Your password change logic here
    return HttpResponse("Password change allowed for admin users.")

# class loginAPI(APIView):
#     @csrf_exempt
#     def post(self,request,*args,**kwargs):
#         if request.method == "POST":
#             obj=request.data
#         # user_name=request.POST.get('mail')
#         # password=request.POST.get('pwd')
#         print(obj)
#         user_name=obj['email']
#         password=obj['password']

#         obj2=CustomUser.objects.filter(email=user_name,password=password)
#         print(obj2)
#         if obj2 :
#             return Response({'res':'ok'})
#             # return render(request,'dashboard.html',{'user_name':user_name})
#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST)