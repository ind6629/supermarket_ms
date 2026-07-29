"""
用户认证视图
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404

from apps.users.models import User
from ..serializers import (
    LoginSerializer, UserSerializer, UserCreateSerializer,
    UserUpdateSerializer, ChangePasswordSerializer, ResetPasswordSerializer,
    UserRegisterSerializer
)
from ..permissions import IsAdmin, IsOwnerOrAdmin, IsActiveUser


class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': '登录成功',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            })
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """用户注册申请视图"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '注册申请已提交，请等待管理员审核'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """用户登出视图"""
    permission_classes = [IsAuthenticated, IsActiveUser]
    
    def post(self, request):
        logout(request)
        return Response({'message': '登出成功'})


class RefreshTokenView(APIView):
    """刷新Token视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'refresh token不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            
            return Response({
                'access': new_access_token
            })
        except Exception as e:
            return Response({'error': '无效的refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """用户个人资料视图"""
    permission_classes = [IsAuthenticated, IsActiveUser]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """修改密码视图"""
    permission_classes = [IsAuthenticated, IsActiveUser]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({'error': {'old_password': '原密码错误'}}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            return Response({'message': '密码修改成功'})
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListCreateAPIView):
    """用户列表视图（管理员专用）"""
    queryset = User.objects.filter(status=User.Status.ACTIVE)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['role', 'department', 'status']
    search_fields = ['username', 'employee_id', 'phone', 'email', 'department']
    ordering_fields = ['create_time', 'update_time', 'last_login']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.soft_delete(request.user)
        return Response({'message': '用户删除成功'}, status=status.HTTP_204_NO_CONTENT)


class ResetUserPasswordView(APIView):
    """重置用户密码视图（管理员专用）"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user.reset_password(serializer.validated_data['new_password'], request.user)
            return Response({'message': '密码重置成功'})
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    """激活用户视图"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.activate(request.user)
        return Response({'message': '用户激活成功'})


class DeactivateUserView(APIView):
    """停用用户视图"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.deactivate(request.user)
        return Response({'message': '用户停用成功'})
