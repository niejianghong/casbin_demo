import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  List,
  Avatar,
  Tag,
  Space,
  Typography,
  Divider,
  Spin
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  SafetyCertificateOutlined,
  AppstoreOutlined,
  BankOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../utils/store';
import { userService } from '../services/user';
import { roleService } from '../services/role';
import { resourceService } from '../services/resource';
import { enterpriseService } from '../services/enterprise';

const { Title, Text } = Typography;

interface DashboardStats {
  totalUsers: number;
  totalRoles: number;
  totalResources: number;
  totalEnterprises: number;
  activeUsers: number;
  activeRoles: number;
}

interface RecentActivity {
  id: string;
  type: string;
  description: string;
  time: string;
  user: string;
}

const Dashboard: React.FC = () => {
  const { user, enterpriseCode } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    totalRoles: 0,
    totalResources: 0,
    totalEnterprises: 0,
    activeUsers: 0,
    activeRoles: 0
  });
  const [loading, setLoading] = useState(true);
  const [recentActivities] = useState<RecentActivity[]>([
    {
      id: '1',
      type: 'user',
      description: '新用户注册',
      time: '2024-01-15 10:30',
      user: 'admin'
    },
    {
      id: '2',
      type: 'role',
      description: '角色权限更新',
      time: '2024-01-15 09:15',
      user: 'admin'
    },
    {
      id: '3',
      type: 'resource',
      description: '新增资源',
      time: '2024-01-15 08:45',
      user: 'admin'
    },
    {
      id: '4',
      type: 'enterprise',
      description: '企业信息更新',
      time: '2024-01-14 16:20',
      user: 'admin'
    }
  ]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // 这里可以调用实际的API获取统计数据
      // 目前使用模拟数据
      setStats({
        totalUsers: 156,
        totalRoles: 24,
        totalResources: 89,
        totalEnterprises: 12,
        activeUsers: 142,
        activeRoles: 22
      });
    } catch (error) {
      console.error('获取仪表板数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'user':
        return <UserOutlined style={{ color: '#1890ff' }} />;
      case 'role':
        return <SafetyCertificateOutlined style={{ color: '#52c41a' }} />;
      case 'resource':
        return <AppstoreOutlined style={{ color: '#faad14' }} />;
      case 'enterprise':
        return <BankOutlined style={{ color: '#722ed1' }} />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'user':
        return 'blue';
      case 'role':
        return 'green';
      case 'resource':
        return 'orange';
      case 'enterprise':
        return 'purple';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>加载中...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 欢迎信息 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Title level={3} style={{ margin: 0 }}>
              欢迎回来，{user?.nick_name || user?.user_name || '用户'}！
            </Title>
            <Text type="secondary">
              当前企业：{enterpriseCode} | 登录时间：{new Date().toLocaleString()}
            </Text>
          </Col>
          <Col>
            <Tag color={user?.is_admin ? 'red' : 'blue'}>
              {user?.is_admin ? '超级管理员' : '普通用户'}
            </Tag>
          </Col>
        </Row>
      </Card>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={stats.totalUsers}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: '8px' }}>
              <Text type="secondary">活跃用户：{stats.activeUsers}</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总角色数"
              value={stats.totalRoles}
              prefix={<SafetyCertificateOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: '8px' }}>
              <Text type="secondary">活跃角色：{stats.activeRoles}</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总资源数"
              value={stats.totalResources}
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
            <div style={{ marginTop: '8px' }}>
              <Text type="secondary">菜单：{Math.floor(stats.totalResources * 0.6)}</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总企业数"
              value={stats.totalEnterprises}
              prefix={<BankOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: '8px' }}>
              <Text type="secondary">活跃企业：{stats.totalEnterprises}</Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 主要内容区域 */}
      <Row gutter={[16, 16]}>
        {/* 最近活动 */}
        <Col xs={24} lg={12}>
          <Card title="最近活动" extra={<a href="#">查看全部</a>}>
            <List
              itemLayout="horizontal"
              dataSource={recentActivities}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={getActivityIcon(item.type)} />}
                    title={
                      <Space>
                        <Text strong>{item.description}</Text>
                        <Tag color={getActivityColor(item.type)}>
                          {item.type === 'user' ? '用户' : 
                           item.type === 'role' ? '角色' : 
                           item.type === 'resource' ? '资源' : '企业'}
                        </Tag>
                      </Space>
                    }
                    description={
                      <Space>
                        <Text type="secondary">操作人：{item.user}</Text>
                        <Text type="secondary">时间：{item.time}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 系统信息 */}
        <Col xs={24} lg={12}>
          <Card title="系统信息">
            <List size="small">
              <List.Item>
                <Text strong>系统名称：</Text>
                <Text>自定义权限管理系统</Text>
              </List.Item>
              <List.Item>
                <Text strong>版本号：</Text>
                <Text>v1.0.0</Text>
              </List.Item>
              <List.Item>
                <Text strong>当前用户：</Text>
                <Text>{user?.user_name}</Text>
              </List.Item>
              <List.Item>
                <Text strong>用户ID：</Text>
                <Text>{user?.user_id}</Text>
              </List.Item>
              <List.Item>
                <Text strong>用户状态：</Text>
                <Tag color={user?.status === 0 ? 'green' : 'red'}>
                  {user?.status === 0 ? '正常' : '禁用'}
                </Tag>
              </List.Item>
              <List.Item>
                <Text strong>当前企业：</Text>
                <Text>{enterpriseCode}</Text>
              </List.Item>
            </List>
          </Card>
        </Col>
      </Row>

      {/* 快速操作 */}
      <Card title="快速操作" style={{ marginTop: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" hoverable style={{ textAlign: 'center' }}>
              <UserOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <div style={{ marginTop: '8px' }}>用户管理</div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" hoverable style={{ textAlign: 'center' }}>
              <SafetyCertificateOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
              <div style={{ marginTop: '8px' }}>角色管理</div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" hoverable style={{ textAlign: 'center' }}>
              <AppstoreOutlined style={{ fontSize: '24px', color: '#faad14' }} />
              <div style={{ marginTop: '8px' }}>资源管理</div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" hoverable style={{ textAlign: 'center' }}>
              <BankOutlined style={{ fontSize: '24px', color: '#722ed1' }} />
              <div style={{ marginTop: '8px' }}>企业管理</div>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Dashboard; 