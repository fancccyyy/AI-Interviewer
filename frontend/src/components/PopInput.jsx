import React, { useState, useContext } from 'react';
import { Button, Form, Input, Modal } from 'antd';
import { InterviewContext } from '../Interview';

const App = () => {
  const [form] = Form.useForm();
  const [formValues, setFormValues] = useState();
  const [open, setOpen] = useState(false);
  const onCreate = values => {
    // console.log('Received values of form: ', values);
    setInterviewStyle(values.style);
    setFormValues(values);
    setOpen(false);
  };
  const { setInterviewStyle } = useContext(InterviewContext);
  return (
    <>
      <Button type="primary" onClick={() => setOpen(true)}>
        切换面试风格
      </Button>
      <pre>{JSON.stringify(formValues, null, 2)}</pre>
      <Modal
        open={open}
        title="请输入您喜欢的面试风格"
        okText="确定"
        cancelText="取消"
        okButtonProps={{ autoFocus: true, htmlType: 'submit' }}
        onCancel={() => setOpen(false)}
        destroyOnHidden
        modalRender={dom => (
          <Form
            layout="vertical"
            form={form}
            name="form_in_modal"
            initialValues={{ modifier: 'public' }}
            clearOnDestroy
            onFinish={values => onCreate(values)}
          >
            {dom}
          </Form>
        )}
      >
        <Form.Item
          name="style"
          label="请输入您喜欢的面试风格，例如：正式、轻松、专业都可以！"
          rules={[{ required: true, message: '请输入您喜欢的面试风格！' }]}
        >
          <Input />
        </Form.Item>
      </Modal>
    </>
  );
};
export default App;