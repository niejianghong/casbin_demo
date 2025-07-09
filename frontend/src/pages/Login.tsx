import React, { useState } from 'react';
import { Form, Input, Button, Card, Select, message } from 'antd';
import { UserOutlined, LockOutlined, BankOutlined } from '@ant-design/icons';
import { authService } from '../services/auth';
import { enterpriseService } from '../services/enterprise';
import { useAuthStore } from '../utils/store';
import { Enterprise } from '../types';

const { Option } = Select;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [enterprises, setEnterprises] = useState<Enterprise[]>([]);
  const { setUser, setToken, setEnterpriseCode } = useAuthStore();

  React.useEffect(() => {
    // 获取企业列表
    enterpriseService.getActiveEnterprises().then(setEnterprises);
  }, []);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      console.log('登录请求数据:', values);
      const response = await authService.login(values);
      console.log('登录响应:', response);
      
      // 保存到本地存储
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      localStorage.setItem('enterprise_code', response.enterprise_code);
      
      // 更新状态
      setToken(response.access_token);
      setUser(response.user);
      setEnterpriseCode(response.enterprise_code);
      
      console.log('Token已保存:', localStorage.getItem('token'));
      
      message.success('登录成功');
      window.location.href = '/';
    } catch (error: any) {
      console.error('登录失败:', error);
      message.error(error.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h2>Casbin权限管理系统</h2>
          <p>请登录您的账户</p>
        </div>
        
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          initialValues={{
            user_name: 'admin',
            password: 'admin123',
            enterprise_code: 'default'
          }}
        >
          <Form.Item
            name="user_name"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="用户名" 
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="enterprise_code"
            rules={[{ required: true, message: '请选择企业!' }]}
          >
            <Select
              placeholder="选择企业"
              size="large"
            >
              <Option value="default">默认企业</Option>
              {enterprises.map(enterprise => (
                <Option key={enterprise.code} value={enterprise.code}>
                  {enterprise.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              size="large"
              block
            >
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login; 