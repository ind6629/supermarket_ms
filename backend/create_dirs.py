#!/usr/bin/env python
"""
创建用户管理模块目录结构脚本
"""
import os
import sys

def create_user_app_structure():
    """创建用户管理应用的文件结构"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_app_dir = os.path.join(base_dir, 'apps', 'users')
    
    # 创建必要的目录
    directories = [
        os.path.join(user_app_dir, 'migrations'),
        os.path.join(user_app_dir, 'views'),
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 创建必要的文件
    files_to_create = {
        'serializers.py': '序列化器',
        'permissions.py': '权限类',
        'urls.py': 'URL配置',
        'views/__init__.py': '视图初始化',
        'views/auth.py': '认证视图',
        'views/user.py': '用户管理视图',
    }
    
    for filename, description in files_to_create.items():
        filepath = os.path.join(user_app_dir, filename)
        
        if os.path.exists(filepath):
            print(f"⚠️  文件已存在: {filename}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                if filename.endswith('__init__.py'):
                    f.write('')
                else:
                    f.write(f'# {description}文件\n')
            print(f"✅ 创建文件: {filename}")
    
    print(f"\n📁 用户应用结构创建完成!")
    print(f"📁 位置: {user_app_dir}")

if __name__ == '__main__':
    try:
        create_user_app_structure()
    except Exception as e:
        print(f"❌ 创建目录结构时出错: {e}")
        sys.exit(1)