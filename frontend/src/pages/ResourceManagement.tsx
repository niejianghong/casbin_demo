import React, { useState, useEffect } from 'react';
import {
  Tree,
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
  TreeSelect,
  Divider,
  Tabs,
  Table
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, FolderOutlined, FileOutlined, TeamOutlined } from '@ant-design/icons';
import { resourceService } from '../services/resource';
import { enterpriseService } from '../services/enterprise';
import { roleService } from '../services/role';

const { Option } = Select;
const { TreeNode } = Tree;
const { TabPane } = Tabs;

import { Resource, Enterprise, Role } from '../types';

const ResourceManagement: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [treeData, setTreeData] = useState<any[]>([]);
  const [enterprises, setEnterprises] = useState<Enterprise[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingResource, setEditingResource] = useState<Resource | null>(null);
  const [roleModalVisible, setRoleModalVisible] = useState(false);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [resourceRoles, setResourceRoles] = useState<Role[]>([]);
  const [form] = Form.useForm();
  const [roleForm] = Form.useForm();
  const [selectedEnterpriseCodes, setSelectedEnterpriseCodes] = useState<string[]>([]);

  useEffect(() => {
    fetchResources();
    fetchEnterprises();
    fetchRoles();
  }, []);

  const fetchResources = async () => {
    try {
      setLoading(true);
      const response = await resourceService.getResources();
      // 后端返回的数据结构是 { data: { resources: [...] }, pagination: {...} }
      const resourceList = response.data?.resources || [];
      console.log('Resource response:', response);
      console.log('Resource list:', resourceList);
      setResources(resourceList);
      
      // 构建树状数据
      const tree = buildTreeData(resourceList);
      setTreeData(tree);
    } catch (error: any) {
      console.error('获取资源列表失败:', error);
      message.error('获取资源列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchEnterprises = async () => {
    try {
      const response = await enterpriseService.getActiveEnterprises();
      setEnterprises(response || []);
    } catch (error: any) {
      message.error('获取企业列表失败');
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await roleService.getActiveRoles();
      setRoles(response || []);
    } catch (error: any) {
      message.error('获取角色列表失败');
    }
  };

  const handleManageRoles = async (resource: Resource) => {
    setSelectedResource(resource);
    try {
      if (resource.code) {
        const response = await resourceService.getRoleResources(resource.code);
        setResourceRoles(response.data?.resources || []);
        setRoleModalVisible(true);
      }
    } catch (error) {
      message.error('获取资源角色失败');
    }
  };

  const handleAddRoles = async (values: any) => {
    if (!selectedResource || !selectedResource.code) return;
    
    try {
      await resourceService.addResourcesToRole(selectedResource.code, {
        resource_codes: values.resource_codes
      });
      message.success('角色分配成功');
      roleForm.resetFields();
      // 重新获取资源角色列表
      const response = await resourceService.getRoleResources(selectedResource.code);
      setResourceRoles(response.data?.resources || []);
    } catch (error) {
      message.error('角色分配失败');
    }
  };

  const handleRemoveRole = async (roleCode: string) => {
    if (!selectedResource || !selectedResource.code) return;
    
    try {
      await resourceService.removeResourcesFromRole(selectedResource.code, {
        resource_codes: [roleCode]
      });
      message.success('角色移除成功');
      // 重新获取资源角色列表
      const response = await resourceService.getRoleResources(selectedResource.code);
      setResourceRoles(response.data?.resources || []);
    } catch (error) {
      message.error('角色移除失败');
    }
  };

  const buildTreeData = (data: Resource[]): any[] => {
    const map = new Map();
    const result: any[] = [];

    // 创建映射
    data.forEach(item => {
      map.set(item.code, {
        key: item.code,
        title: item.name,
        code: item.code,
        type: item.type,
        status: item.status,
        children: []
      });
    });

    // 构建树结构
    data.forEach(item => {
      const node = map.get(item.code);
      if (item.parent_code && map.has(item.parent_code)) {
        const parent = map.get(item.parent_code);
        parent.children.push(node);
      } else {
        result.push(node);
      }
    });

    // 排序
    const sortNodes = (nodes: any[]) => {
      nodes.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
      nodes.forEach(node => {
        if (node.children && node.children.length > 0) {
          sortNodes(node.children);
        }
      });
    };
    sortNodes(result);

    return result;
  };

  // 获取资源已分配的企业
  const fetchResourceEnterprises = async (resourceCode: string) => {
    try {
      const res = await resourceService.getResourceEnterprises(resourceCode);
      const codes = (res.data?.enterprises || []).map((e: any) => e.enterprise_code);
      setSelectedEnterpriseCodes(codes);
      form.setFieldsValue({ enterprise_codes: codes });
    } catch (error) {
      setSelectedEnterpriseCodes([]);
    }
  };

  // 打开新增/编辑弹窗时，回显企业
  const handleAdd = (parentCode?: string) => {
    setEditingResource(null);
    form.resetFields();
    setSelectedEnterpriseCodes([]);
    if (parentCode) {
      form.setFieldsValue({ parent_code: parentCode });
    }
    setModalVisible(true);
  };

  const handleEdit = (record: Resource) => {
    setEditingResource(record);
    form.setFieldsValue(record);
    if (record.code) {
      fetchResourceEnterprises(record.code);
    } else {
      setSelectedEnterpriseCodes([]);
    }
    setModalVisible(true);
  };

  const handleDelete = async (code: string) => {
    try {
      const resource = resources.find(r => r.code === code);
      if (resource) {
        await resourceService.deleteResource(resource.id);
        message.success('删除资源成功');
        fetchResources();
      }
    } catch (error) {
      message.error('删除资源失败');
    }
  };

  // 提交表单时，先保存资源，再分配企业
  const handleSubmit = async (values: any) => {
    try {
      const submitData = {
        name: values.name,
        code: values.code,
        type: values.type === 'menu' ? 2 : values.type === 'api' ? 1 : 3,
        path: values.path,
        act: values.act,
        parent_code: values.parent_code,
        status: values.status
      };
      let resourceCode = values.code;
      let resourceId = editingResource?.id;
      if (editingResource) {
        await resourceService.updateResource(editingResource.id, submitData);
        message.success('更新资源成功');
      } else {
        const res = await resourceService.createResource(submitData);
        resourceCode = res.code;
        resourceId = res.id;
        message.success('创建资源成功');
      }
      // 分配企业
      if (resourceCode && values.enterprise_codes && values.enterprise_codes.length > 0) {
        await resourceService.assignResourceToEnterprises({
          resource_code: resourceCode,
          enterprise_codes: values.enterprise_codes
        });
      }
      setModalVisible(false);
      fetchResources();
    } catch (error: any) {
      console.error('提交失败:', error);
      message.error(editingResource ? '更新资源失败' : '创建资源失败');
    }
  };

  const renderTreeNodes = (data: any[]): any[] => {
    return data.map(node => {
      const title = (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <span>
            {node.type === 'menu' ? <FolderOutlined /> : <FileOutlined />}
            <span style={{ marginLeft: 8 }}>{node.title}</span>
            <Tag style={{ marginLeft: 8 }}>
              {node.type === 'menu' ? '菜单' : node.type === 'api' ? 'API' : '代理'}
            </Tag>
          </span>
          <Space size="small">
            <Button
              type="link"
              size="small"
              icon={<PlusOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                handleAdd(node.code);
              }}
            >
              添加子级
            </Button>
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                const resource = resources.find(r => r.code === node.code);
                if (resource) handleEdit(resource);
              }}
            >
              编辑
            </Button>
            <Button
              type="link"
              size="small"
              icon={<TeamOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                const resource = resources.find(r => r.code === node.code);
                if (resource) handleManageRoles(resource);
              }}
            >
              管理角色
            </Button>
            <Popconfirm
              title="确定要删除这个资源吗？"
              onConfirm={(e) => {
                e?.stopPropagation();
                handleDelete(node.code);
              }}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                onClick={(e) => e.stopPropagation()}
              >
                删除
              </Button>
            </Popconfirm>
          </Space>
        </div>
      );

      return (
        <TreeNode
          key={node.key}
          title={title}
          icon={node.type === 'menu' ? <FolderOutlined /> : <FileOutlined />}
        >
          {node.children && node.children.length > 0 && renderTreeNodes(node.children)}
        </TreeNode>
      );
    });
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="资源管理" extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => handleAdd()}>
          新增资源
        </Button>
      }>
        <Row gutter={24}>
          <Col span={16}>
            <Card title="资源树" size="small">
              <Tree
                showIcon
                defaultExpandAll
              >
                {renderTreeNodes(treeData)}
              </Tree>
            </Card>
          </Col>
          <Col span={8}>
            <Card title="资源列表" size="small">
              <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                {resources.map(resource => (
                  <div
                    key={resource.code}
                    style={{
                      padding: '8px',
                      border: '1px solid #f0f0f0',
                      marginBottom: '8px',
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{resource.name}</div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {resource.code} | {resource.type}
                      </div>
                    </div>
                    <Tag color={resource.status === 0 ? 'green' : 'red'}>
                      {resource.status === 0 ? '正常' : '禁用'}
                    </Tag>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      </Card>

      <Modal
        title={editingResource ? '编辑资源' : '新增资源'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
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
                label="资源名称"
                rules={[{ required: true, message: '请输入资源名称' }]}
              >
                <Input placeholder="请输入资源名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="code"
                label="资源代码"
                rules={[{ required: true, message: '请输入资源代码' }]}
              >
                <Input placeholder="请输入资源代码" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="type"
                label="资源类型"
                rules={[{ required: true, message: '请选择资源类型' }]}
              >
                <Select placeholder="请选择资源类型">
                  <Option value="menu">菜单</Option>
                  <Option value="api">API</Option>
                  <Option value="agent">代理</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="parent_code"
                label="父级资源"
              >
                <TreeSelect
                  placeholder="请选择父级资源"
                  allowClear
                  treeData={treeData.map(node => ({
                    title: node.title,
                    value: node.code,
                    children: node.children?.map((child: any) => ({
                      title: child.title,
                      value: child.code
                    }))
                  }))}
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="path"
                label="路径"
              >
                <Input placeholder="请输入资源路径" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="act"
                label="操作"
              >
                <Input placeholder="请输入操作类型" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="enterprise_codes"
                label="所属企业"
                rules={[{ required: true, message: '请选择所属企业' }]}
              >
                <Select
                  mode="multiple"
                  placeholder="请选择企业"
                  value={selectedEnterpriseCodes}
                  onChange={setSelectedEnterpriseCodes}
                  showSearch
                  optionFilterProp="children"
                >
                  {enterprises.map(ent => (
                    <Option key={ent.code} value={ent.code}>{ent.name} ({ent.code})</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
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
                {editingResource ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 管理角色模态框 */}
      <Modal
        title={`管理资源 ${selectedResource?.name} 的角色`}
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
                name="resource_codes"
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
                      onConfirm={() => handleRemoveRole(record.code)}
                    >
                      <Button type="link" danger>
                        移除
                      </Button>
                    </Popconfirm>
                  )
                }
              ]}
              dataSource={resourceRoles}
              rowKey="id"
              pagination={false}
            />
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
};

export default ResourceManagement; 