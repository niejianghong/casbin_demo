import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Tag,
  InputNumber,
  Tabs
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, UserOutlined } from '@ant-design/icons';
import { roleService } from '../services/role';
import { enterpriseService } from '../services/enterprise';
import { userService } from '../services/user';

const { Option } = Select;
const { TabPane } = Tabs;

import { Role, User } from '../types';

interface Enterprise {
  code: string;
  name: string;
  status: number;
}

const RoleManagement: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [enterprises, setEnterprises] = useState<Enterprise[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [roleUsers, setRoleUsers] = useState<User[]>([]);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();
  const [userForm] = Form.useForm();

  useEffect(() => {
    fetchRoles();
    fetchUsers();
  }, []);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await roleService.getRoles();
      // 后端返回的数据结构是 { data: { roles: [...] }, pagination: {...} }
      setRoles(response.data?.roles || []);
    } catch (error) {
      message.error('获取角色列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchEnterprises = async () => {
    try {
      const response = await enterpriseService.getActiveEnterprises();
      setEnterprises(response || []);
    } catch (error) {
      message.error('获取企业列表失败');
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await userService.getUsers();
      setUsers(response.data?.users || []);
    } catch (error) {
      message.error('获取用户列表失败');
    }
  };

  const handleSearch = async (values: any) => {
    try {
      setLoading(true);
      const response = await roleService.getRoles();
      setRoles(response.data?.roles || []);
    } catch (error) {
      message.error('搜索角色失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    setEditingRole(null);
    form.resetFields();
    await fetchEnterprises(); // 等待企业数据加载
    setModalVisible(true);
  };

  const handleEdit = (record: Role) => {
    setEditingRole(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await roleService.deleteRole(id);
      message.success('删除角色成功');
      fetchRoles();
    } catch (error) {
      message.error('删除角色失败');
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingRole) {
        await roleService.updateRole(editingRole.id, values);
        message.success('更新角色成功');
      } else {
        await roleService.createRole(values);
        message.success('创建角色成功');
      }
      setModalVisible(false);
      fetchRoles();
    } catch (error) {
      message.error(editingRole ? '更新角色失败' : '创建角色失败');
    }
  };

  const handleManageUsers = async (role: Role) => {
    setSelectedRole(role);
    try {
      const response = await roleService.getRoleUsers(role.id);
      setRoleUsers(response.data?.users || []);
      setUserModalVisible(true);
    } catch (error) {
      message.error('获取角色用户失败');
    }
  };

  const handleAddUsers = async (values: any) => {
    if (!selectedRole) return;
    
    try {
      await roleService.assignUsersToRole(selectedRole.id, {
        user_ids: values.user_ids
      });
      message.success('用户分配成功');
      userForm.resetFields();
      // 重新获取角色用户列表
      const response = await roleService.getRoleUsers(selectedRole.id);
      setRoleUsers(response.data?.users || []);
    } catch (error) {
      message.error('用户分配失败');
    }
  };

  const handleRemoveUser = async (userId: number) => {
    if (!selectedRole) return;
    
    try {
      await roleService.removeUsersFromRole(selectedRole.id, {
        user_ids: [userId]
      });
      message.success('用户移除成功');
      // 重新获取角色用户列表
      const response = await roleService.getRoleUsers(selectedRole.id);
      setRoleUsers(response.data?.users || []);
    } catch (error) {
      message.error('用户移除失败');
    }
  };

  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '角色代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '所属企业',
      dataIndex: 'enterprise_code',
      key: 'enterprise_code',
      render: (enterprise_code: string) => {
        const enterprise = enterprises.find(e => e.code === enterprise_code);
        return enterprise ? enterprise.name : enterprise_code;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: number) => (
        <Tag color={status === 0 ? 'green' : 'red'}>
          {status === 0 ? '正常' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Role) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<UserOutlined />}
            onClick={() => handleManageUsers(record)}
          >
            管理用户
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个角色吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card title="角色管理" extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增角色
        </Button>
      }>
        <Form
          form={searchForm}
          layout="inline"
          onFinish={handleSearch}
          style={{ marginBottom: '16px' }}
        >
          <Form.Item name="name" label="角色名称">
            <Input placeholder="请输入角色名称" allowClear />
          </Form.Item>
          <Form.Item name="code" label="角色代码">
            <Input placeholder="请输入角色代码" allowClear />
          </Form.Item>
          <Form.Item name="enterprise_code" label="所属企业">
            <Select placeholder="请选择企业" allowClear style={{ width: 200 }}>
              {enterprises.map(enterprise => (
                <Option key={enterprise.code} value={enterprise.code}>
                  {enterprise.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select placeholder="请选择状态" allowClear style={{ width: 120 }}>
              <Option value={0}>正常</Option>
              <Option value={1}>禁用</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} htmlType="submit">
                搜索
              </Button>
              <Button onClick={() => {
                searchForm.resetFields();
                fetchRoles();
              }}>
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>

        <Table
          columns={columns}
          dataSource={roles}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title={editingRole ? '编辑角色' : '新增角色'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label="角色名称"
                rules={[{ required: true, message: '请输入角色名称' }]}
              >
                <Input placeholder="请输入角色名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="code"
                label="角色代码"
                rules={[{ required: true, message: '请输入角色代码' }]}
              >
                <Input placeholder="请输入角色代码" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea rows={3} placeholder="请输入角色描述" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="enterprise_code"
                label="所属企业"
                rules={[{ required: true, message: '请选择所属企业' }]}
              >
                <Select placeholder="请选择企业">
                  {enterprises.map(enterprise => (
                    <Option key={enterprise.code} value={enterprise.code}>
                      {enterprise.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="status"
                label="状态"
                rules={[{ required: true, message: '请选择状态' }]}
                initialValue={0}
              >
                <Select>
                  <Option value={0}>正常</Option>
                  <Option value={1}>禁用</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingRole ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 管理用户模态框 */}
      <Modal
        title={`管理角色 ${selectedRole?.name} 的用户`}
        open={userModalVisible}
        onCancel={() => setUserModalVisible(false)}
        width={800}
        footer={null}
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab="添加用户" key="1">
            <Form
              form={userForm}
              layout="vertical"
              onFinish={handleAddUsers}
            >
              <Form.Item
                name="user_ids"
                label="选择用户"
                rules={[{ required: true, message: '请选择用户' }]}
              >
                <Select
                  mode="multiple"
                  placeholder="请选择用户"
                  showSearch
                  optionFilterProp="children"
                >
                  {users.map(user => (
                    <Option key={user.user_id} value={user.user_id}>
                      {user.user_name} ({user.email})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">
                    添加用户
                  </Button>
                  <Button onClick={() => setUserModalVisible(false)}>
                    取消
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>
          <TabPane tab="当前用户" key="2">
            <Table
              columns={[
                { title: '用户ID', dataIndex: 'user_id' },
                { title: '用户名', dataIndex: 'user_name' },
                { title: '邮箱', dataIndex: 'email' },
                { title: '昵称', dataIndex: 'nick_name' },
                {
                  title: '操作',
                  key: 'action',
                  render: (_: any, record: User) => (
                    <Popconfirm
                      title="确定要移除这个用户吗？"
                      onConfirm={() => handleRemoveUser(record.user_id)}
                    >
                      <Button type="link" danger>
                        移除
                      </Button>
                    </Popconfirm>
                  )
                }
              ]}
              dataSource={roleUsers}
              rowKey="user_id"
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
};

export default RoleManagement; 