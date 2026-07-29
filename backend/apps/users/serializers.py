"""
用户序列化器
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器（用于列表和详情）"""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'employee_id', 'email', 'phone', 
            'gender', 'gender_display', 'role', 'role_display',
            'avatar', 'department', 'position',
            'last_login', 'last_login_ip', 'last_login_time',
            'date_joined', 'is_active', 'is_staff', 'is_superuser',
            'status', 'status_display', 'approval_status', 'approval_status_display',
            'review_remark', 'review_time', 'create_time', 'update_time', 'remark'
        ]
        read_only_fields = [
            'id', 'last_login', 'last_login_ip', 'last_login_time',
            'date_joined', 'create_time', 'update_time'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=6
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'employee_id', 'password', 'confirm_password',
            'email', 'phone', 'gender', 'role', 'avatar',
            'department', 'position', 'status', 'remark'
        ]
        extra_kwargs = {
            'username': {'required': True, 'min_length': 3},
            'employee_id': {'required': True},
            'email': {'required': True},
            'phone': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "用户名已存在"})
        
        if User.objects.filter(employee_id=attrs['employee_id']).exists():
            raise serializers.ValidationError({"employee_id": "工号已存在"})
        
        if User.objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError({"phone": "手机号已存在"})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "邮箱已存在"})
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            employee_id=validated_data['employee_id'],
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', User.Role.CASHIER),
            gender=validated_data.get('gender', User.Gender.UNKNOWN),
            department=validated_data.get('department', ''),
            position=validated_data.get('position', ''),
            avatar=validated_data.get('avatar', None),
            status=validated_data.get('status', User.Status.ACTIVE),
            approval_status=User.ApprovalStatus.APPROVED,
            remark=validated_data.get('remark', '')
        )
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user.create_by = request.user
            user.save()
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    
    class Meta:
        model = User
        fields = [
            'username', 'employee_id', 'email', 'phone', 'gender',
            'role', 'avatar', 'department', 'position', 'status', 'remark'
        ]
        read_only_fields = ['employee_id']
    
    def validate(self, attrs):
        instance = self.instance
        
        if 'username' in attrs and User.objects.filter(username=attrs['username']).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"username": "用户名已存在"})
        
        if 'phone' in attrs and User.objects.filter(phone=attrs['phone']).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"phone": "手机号已存在"})
        
        if 'email' in attrs and User.objects.filter(email=attrs['email']).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"email": "邮箱已存在"})
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'},
        min_length=6
    )
    confirm_password = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "新密码不能与旧密码相同"})
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    new_password = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'},
        min_length=6
    )
    confirm_password = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return attrs


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册申请序列化器"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email', 'phone', 'gender', 'remark']
        extra_kwargs = {
            'username': {'required': True, 'min_length': 3},
            'email': {'required': True},
            'phone': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': '两次输入的密码不一致'})

        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': '用户名已存在'})

        if User.objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError({'phone': '手机号已存在'})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': '邮箱已存在'})

        return attrs

    def _generate_employee_id(self):
        while True:
            employee_id = f"REG{timezone.now().strftime('%Y%m%d%H%M%S%f')[-12:]}"
            if not User.objects.filter(employee_id=employee_id).exists():
                return employee_id

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            employee_id=self._generate_employee_id(),
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            gender=validated_data.get('gender', User.Gender.UNKNOWN),
            role=User.Role.CASHIER,
            status=User.Status.INACTIVE,
            approval_status=User.ApprovalStatus.PENDING,
            is_active=False,
            remark=validated_data.get('remark', '注册申请'),
        )
        return user


class UserReviewSerializer(serializers.Serializer):
    """用户注册审核序列化器"""
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)
    review_remark = serializers.CharField(required=False, allow_blank=True, max_length=200)

    def validate(self, attrs):
        if attrs['action'] == 'approve' and attrs.get('role') in [None, '']:
            raise serializers.ValidationError({'role': '审核通过时必须分配角色'})
        return attrs


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("用户名和密码不能为空")

        user_obj = (
            User.objects.filter(username=username).first()
            or User.objects.filter(phone=username).first()
            or User.objects.filter(email=username).first()
        )

        if user_obj and user_obj.check_password(password):
            if user_obj.approval_status == User.ApprovalStatus.PENDING:
                raise serializers.ValidationError("注册申请待管理员审核，请稍后再登录")
            if user_obj.approval_status == User.ApprovalStatus.REJECTED:
                raise serializers.ValidationError("注册申请已被驳回，请联系管理员")
            if not user_obj.is_active:
                raise serializers.ValidationError("用户账户已被禁用")
            if user_obj.status != User.Status.ACTIVE:
                raise serializers.ValidationError("用户账户已被停用")

        user = authenticate(username=user_obj.username if user_obj else username, password=password)
        if not user:
            raise serializers.ValidationError("用户名或密码错误")

        if user.approval_status == User.ApprovalStatus.PENDING:
            raise serializers.ValidationError("注册申请待管理员审核，请稍后再登录")
        if user.approval_status == User.ApprovalStatus.REJECTED:
            raise serializers.ValidationError("注册申请已被驳回，请联系管理员")
        if not user.is_active:
            raise serializers.ValidationError("用户账户已被禁用")
        if user.status != User.Status.ACTIVE:
            raise serializers.ValidationError("用户账户已被停用")

        attrs['user'] = user
        return attrs
