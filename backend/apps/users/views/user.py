"""
用户管理视图
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from apps.users.models import User
from apps.operations.models import OperationLog
from ..serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer, ResetPasswordSerializer, UserReviewSerializer
)
from ..permissions import IsAdmin, IsOwnerOrAdmin


class UserListView(generics.ListCreateAPIView):
    """用户列表视图（管理员专用）"""
    queryset = User.objects.exclude(status=User.Status.DELETED)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()

        search = self.request.query_params.get('search')
        role = self.request.query_params.get('role')
        status_param = self.request.query_params.get('status')
        approval_status = self.request.query_params.get('approval_status')

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(employee_id__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
            )

        if role not in [None, '']:
            queryset = queryset.filter(role=role)

        if status_param not in [None, '']:
            queryset = queryset.filter(status=status_param)

        if approval_status not in [None, '']:
            queryset = queryset.filter(approval_status=approval_status)

        return queryset.order_by('-date_joined')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            OperationLog.objects.create(
                user=request.user,
                action_type=OperationLog.ActionType.CREATE,
                model_name='User',
                object_id=str(response.data['id']),
                object_repr=response.data.get('username', ''),
                action_detail='创建新用户',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            OperationLog.objects.create(
                user=request.user,
                action_type=OperationLog.ActionType.UPDATE,
                model_name='User',
                object_id=str(kwargs.get('pk')),
                object_repr=response.data.get('username', ''),
                action_detail='更新用户信息',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        
        user.soft_delete(request.user)
        
        OperationLog.objects.create(
            user=request.user,
            action_type=OperationLog.ActionType.DELETE,
            model_name='User',
            object_id=str(kwargs.get('pk')),
            object_repr=str(user),
            action_detail='删除用户',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': '用户删除成功'}, status=status.HTTP_204_NO_CONTENT)


class ResetUserPasswordView(APIView):
    """重置用户密码视图（管理员专用）"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user.reset_password(serializer.validated_data['new_password'], request.user)
            
            OperationLog.objects.create(
                user=request.user,
                action_type=OperationLog.ActionType.UPDATE,
                model_name='User',
                object_id=str(user.id),
                object_repr=str(user),
                action_detail='重置用户密码',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({'message': '密码重置成功'})
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    """激活用户视图"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.activate(request.user)
        
        OperationLog.objects.create(
            user=request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='User',
            object_id=str(user.id),
            object_repr=str(user),
            action_detail='激活用户',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': '用户激活成功'})


class DeactivateUserView(APIView):
    """停用用户视图"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.deactivate(request.user)
        
        OperationLog.objects.create(
            user=request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='User',
            object_id=str(user.id),
            object_repr=str(user),
            action_detail='停用用户',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': '用户停用成功'})


class ReviewUserRegistrationView(APIView):
    """审核注册申请并分配角色"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        if user.approval_status == User.ApprovalStatus.APPROVED:
            return Response({'error': '该用户已审核通过'}, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data['action']
        review_remark = serializer.validated_data.get('review_remark', '')

        if action == 'approve':
            user.role = int(serializer.validated_data['role'])
            user.approval_status = User.ApprovalStatus.APPROVED
            user.review_remark = review_remark
            user.review_time = timezone.now()
            user.status = User.Status.ACTIVE
            user.is_active = True
            user.update_by = request.user
            user.save(
                update_fields=[
                    'role',
                    'approval_status',
                    'review_remark',
                    'review_time',
                    'status',
                    'is_active',
                    'update_by',
                    'update_time',
                ]
            )
            action_detail = f'审核通过注册申请，分配角色：{user.get_role_display()}'
            message = '审核通过，角色分配成功'
        else:
            user.approval_status = User.ApprovalStatus.REJECTED
            user.review_remark = review_remark
            user.review_time = timezone.now()
            user.status = User.Status.INACTIVE
            user.is_active = False
            user.update_by = request.user
            user.save(
                update_fields=[
                    'approval_status',
                    'review_remark',
                    'review_time',
                    'status',
                    'is_active',
                    'update_by',
                    'update_time',
                ]
            )
            action_detail = '驳回注册申请'
            message = '已驳回该注册申请'

        OperationLog.objects.create(
            user=request.user,
            action_type=OperationLog.ActionType.UPDATE,
            model_name='User',
            object_id=str(user.id),
            object_repr=str(user),
            action_detail=action_detail,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({'message': message, 'user': UserSerializer(user).data})