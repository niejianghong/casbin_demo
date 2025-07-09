import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  message,
  Space,
  Tag,
  Popconfirm,
  Tabs,
  Transfer,
  Typography
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined, TeamOutlined } from '@ant-design/icons';
import { enterpriseService } from '../services/enterprise';
import { userService } from '../services/user';
import { roleService } from '../services/role';
import { Enterprise, User, Role } from '../types';

const { Title } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const EnterpriseManagement: React.FC = () => {
  const [enterprises, setEnterprises] = useState<Enterprise[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [enterpriseUsers, setEnterpriseUsers] = useState<User[]>([]);
  const [enterpriseRoles, setEnterpriseRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [roleModalVisible, setRoleModalVisible] = useState(false);
  const [selectedEnterprise, setSelectedEnterprise] = useState<Enterprise | null>(null);
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
  const [selectedRoleCodes, setSelectedRoleCodes] = useState<string[]>([]);
  const [form] = Form.useForm();
  const [userForm] = Form.useForm();
  const [roleForm] = Form.useForm();

  useEffect(() => {
    fetchEnterprises();
    fetchUsers();
    fetchRoles();
  }, []);

  const fetchEnterprises = async () => {
    setLoading(true);
    try {
      const response = await enterpriseService.getEnterprises();
      setEnterprises(response.data.enterprises || []);
    } catch (error) {
      message.error('获取企业列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await userService.getUsers();
      setUsers(response.data.users || []);
    } catch (error) {
      message.error('获取用户列表失败');
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await roleService.getActiveRoles();
      setRoles(response || []);
    } catch (error) {
      message.error('获取角色列表失败');
    }
  };

  const fetchEnterpriseUsers = async (enterpriseCode: string) => {
    try {
      const response = await enterpriseService.getEnterpriseUsers(enterpriseCode);
      setEnterpriseUsers(response.data.users || []);
    } catch (error) {
      message.error('获取企业用户失败');
    }
  };

  const fetchEnterpriseRoles = async (enterpriseCode: string) => {
    try {
      const response = await enterpriseService.getEnterpriseRoles(enterpriseCode);
      setEnterpriseRoles(response.data.roles || []);
    } catch (error) {
      message.error('获取企业角色失败');
    }
  };

  const handleCreateEnterprise = async (values: any) => {
    try {
      await enterpriseService.createEnterprise(values);
      message.success('企业创建成功');
      setModalVisible(false);
      form.resetFields();
      fetchEnterprises();
    } catch (error) {
      message.error('企业创建失败');
    }
  };

  const handleAddUsers = async (values: any) => {
    if (!selectedEnterprise) return;
    
    try {
      await enterpriseService.addUsersToEnterprise(selectedEnterprise.code, {
        user_ids: values.user_ids,
        status: 0
      });
      message.success('用户添加成功');
      setUserModalVisible(false);
      userForm.resetFields();
      fetchEnterpriseUsers(selectedEnterprise.code);
    } catch (error) {
      message.error('用户添加失败');
    }
  };

  const handleAddRoles = async (values: any) => {
    if (!selectedEnterprise) return;
    
    try {
      await enterpriseService.addRolesToEnterprise(selectedEnterprise.code, {
        role_codes: values.role_codes
      });
      message.success('角色添加成功');
      setRoleModalVisible(false);
      roleForm.resetFields();
      fetchEnterpriseRoles(selectedEnterprise.code);
    } catch (error) {
      message.error('角色添加失败');
    }
  };

  const showUserModal = (enterprise: Enterprise) => {
    setSelectedEnterprise(enterprise);
    fetchEnterpriseUsers(enterprise.code);
    setUserModalVisible(true);
  };

  const showRoleModal = (enterprise: Enterprise) => {
    setSelectedEnterprise(enterprise);
    fetchEnterpriseRoles(enterprise.code);
    setRoleModalVisible(true);
  };

  const columns = [
    {
      title: '企业ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '企业代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '企业名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
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
      title: '操作',
      key: 'action',
      render: (_: any, record: Enterprise) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<UserOutlined />}
            onClick={() => showUserModal(record)}
          >
            管理用户
          </Button>
          <Button
            type="link"
            icon={<TeamOutlined />}
            onClick={() => showRoleModal(record)}
          >
            管理角色
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => {
              setSelectedEnterprise(record);
              form.setFieldsValue(record);
              setModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个企业吗？"
            onConfirm={() => {
              // 删除企业逻辑
            }}
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
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <Title level={3}>企业管理</Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setSelectedEnterprise(null);
              form.resetFields();
              setModalVisible(true);
            }}
          >
            创建企业
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={enterprises}
          rowKey="id"
          loading={loading}
          pagination={{
            total: enterprises.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>

      {/* 创建/编辑企业模态框 */}
      <Modal
        title={selectedEnterprise ? '编辑企业' : '创建企业'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateEnterprise}
        >
          <Form.Item
            name="code"
            label="企业代码"
            rules={[{ required: true, message: '请输入企业代码' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="name"
            label="企业名称"
            rules={[{ required: true, message: '请输入企业名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description"
            label="企业描述"
          >
            <Input.TextArea />
          </Form.Item>
          <Form.Item
            name="status"
            label="状态"
          >
            <Select>
              <Option value={0}>正常</Option>
              <Option value={1}>禁用</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {selectedEnterprise ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 管理用户模态框 */}
      <Modal
        title={`管理企业 ${selectedEnterprise?.name} 的用户`}
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
                      onConfirm={() => {
                        if (selectedEnterprise) {
                          enterpriseService.removeUsersFromEnterprise(selectedEnterprise.code, {
                            user_ids: [record.user_id]
                          }).then(() => {
                            message.success('用户移除成功');
                            fetchEnterpriseUsers(selectedEnterprise.code);
                          }).catch(() => {
                            message.error('用户移除失败');
                          });
                        }
                      }}
                    >
                      <Button type="link" danger>
                        移除
                      </Button>
                    </Popconfirm>
                  )
                }
              ]}
              dataSource={enterpriseUsers}
              rowKey="user_id"
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Modal>

      {/* 管理角色模态框 */}
      <Modal
        title={`管理企业 ${selectedEnterprise?.name} 的角色`}
        open={roleModalVisible}
        onCancel={() => setRoleModalVisible(false)}
        width={800}
        footer={null}
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab="添加角色" key="1">
            <Form
              form={roleForm}
              layout="vertical"
              onFinish={handleAddRoles}
            >
              <Form.Item
                name="role_codes"
                label="选择角色"
                rules={[{ required: true, message: '请选择角色' }]}
              >
                <Select
                  mode="multiple"
                  placeholder="请选择角色"
                  showSearch
                  optionFilterProp="children"
                >
                  {roles.map(role => (
                    <Option key={role.code} value={role.code}>
                      {role.name} ({role.code})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">
                    添加角色
                  </Button>
                  <Button onClick={() => setRoleModalVisible(false)}>
                    取消
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>
          <TabPane tab="当前角色" key="2">
            <Table
              columns={[
                { title: '角色ID', dataIndex: 'id' },
                { title: '角色名称', dataIndex: 'name' },
                { title: '角色代码', dataIndex: 'code' },
                { title: '描述', dataIndex: 'description' },
                {
                  title: '操作',
                  key: 'action',
                  render: (_: any, record: Role) => (
                    <Popconfirm
                      title="确定要移除这个角色吗？"
                      onConfirm={() => {
                        if (selectedEnterprise) {
                          enterpriseService.removeRolesFromEnterprise(selectedEnterprise.code, {
                            role_codes: [record.code]
                          }).then(() => {
                            message.success('角色移除成功');
                            fetchEnterpriseRoles(selectedEnterprise.code);
                          }).catch(() => {
                            message.error('角色移除失败');
                          });
                        }
                      }}
                    >
                      <Button type="link" danger>
                        移除
                      </Button>
                    </Popconfirm>
                  )
                }
              ]}
              dataSource={enterpriseRoles}
              rowKey="id"
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
};

export default EnterpriseManagement; 