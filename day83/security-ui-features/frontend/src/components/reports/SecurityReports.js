import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Descriptions, Table, Tabs, Statistic, Row, Col } from 'antd';
import { DownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import { securityApi } from '../../services/api';

function SecurityReports() {
  const [dailyReport, setDailyReport] = useState(null);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [complianceReport, setComplianceReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const [daily, weekly, compliance] = await Promise.all([
        securityApi.getDailyReport(),
        securityApi.getWeeklyReport(),
        securityApi.getComplianceReport()
      ]);
      
      setDailyReport(daily.data);
      setWeeklyReport(weekly.data);
      setComplianceReport(compliance.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading reports:', error);
      setLoading(false);
    }
  };

  const dailyReportTab = (
    <Card>
      {dailyReport && (
        <>
          <Descriptions title="Daily Security Report" bordered column={2}>
            <Descriptions.Item label="Report Date">
              {dailyReport.report_date}
            </Descriptions.Item>
            <Descriptions.Item label="Total Events">
              {dailyReport.total_events}
            </Descriptions.Item>
            <Descriptions.Item label="Critical Events">
              {dailyReport.critical_events}
            </Descriptions.Item>
            <Descriptions.Item label="Resolved Events">
              {dailyReport.resolved_events}
            </Descriptions.Item>
            <Descriptions.Item label="Resolution Rate">
              {dailyReport.resolution_rate}%
            </Descriptions.Item>
          </Descriptions>

          <Card title="Top Event Types" style={{ marginTop: 16 }}>
            <Table
              dataSource={dailyReport.top_event_types}
              columns={[
                { title: 'Event Type', dataIndex: 'event_type', key: 'event_type' },
                { title: 'Count', dataIndex: 'count', key: 'count' },
              ]}
              pagination={false}
              rowKey="event_type"
            />
          </Card>
        </>
      )}
    </Card>
  );

  const weeklyReportTab = (
    <Card>
      {weeklyReport && (
        <>
          <Descriptions title="Weekly Security Report" bordered>
            <Descriptions.Item label="Period">
              {weeklyReport.report_period.start_date} to {weeklyReport.report_period.end_date}
            </Descriptions.Item>
          </Descriptions>

          <Card title="Daily Breakdown" style={{ marginTop: 16 }}>
            <Table
              dataSource={weeklyReport.daily_breakdown}
              columns={[
                { title: 'Date', dataIndex: 'date', key: 'date' },
                { title: 'Total', dataIndex: 'total_events', key: 'total_events' },
                { title: 'Critical', dataIndex: 'critical', key: 'critical' },
                { title: 'High', dataIndex: 'high', key: 'high' },
                { title: 'Medium', dataIndex: 'medium', key: 'medium' },
                { title: 'Low', dataIndex: 'low', key: 'low' },
              ]}
              pagination={false}
              rowKey="date"
            />
          </Card>
        </>
      )}
    </Card>
  );

  const complianceReportTab = (
    <Card>
      {complianceReport && (
        <>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Compliance Status"
                  value={complianceReport.security_events.compliance_status}
                  valueStyle={{ 
                    color: complianceReport.security_events.compliance_status === 'PASS' ? '#3f8600' : '#cf1322' 
                  }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Total Security Events"
                  value={complianceReport.security_events.total}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Critical Unresolved"
                  value={complianceReport.security_events.critical_unresolved}
                  valueStyle={{ 
                    color: complianceReport.security_events.critical_unresolved > 0 ? '#cf1322' : '#3f8600' 
                  }}
                />
              </Card>
            </Col>
          </Row>

          <Card title="Audit Coverage" style={{ marginBottom: 16 }}>
            <Descriptions bordered>
              <Descriptions.Item label="Total Audit Logs">
                {complianceReport.audit_coverage.total_logs}
              </Descriptions.Item>
              <Descriptions.Item label="Coverage Status">
                {complianceReport.audit_coverage.coverage}
              </Descriptions.Item>
              <Descriptions.Item label="Generated At">
                {new Date(complianceReport.generated_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </>
      )}
    </Card>
  );

  const tabItems = [
    {
      key: 'daily',
      label: 'Daily Report',
      children: dailyReportTab,
    },
    {
      key: 'weekly',
      label: 'Weekly Report',
      children: weeklyReportTab,
    },
    {
      key: 'compliance',
      label: 'Compliance Report',
      children: complianceReportTab,
    },
  ];

  return (
    <Card 
      title="Security Reports"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadReports} loading={loading}>
            Refresh
          </Button>
          <Button icon={<DownloadOutlined />} type="primary">
            Export Reports
          </Button>
        </Space>
      }
    >
      <Tabs items={tabItems} />
    </Card>
  );
}

export default SecurityReports;
