import React, { useState } from 'react'
import { TestTube, Send, Zap, AlertCircle, CheckCircle, AlertTriangle, Info } from 'lucide-react'
import useNotificationStore from '../../store/notificationStore'
import toast from 'react-hot-toast'

const TestGenerator = () => {
  const [testType, setTestType] = useState('info')
  const [customTitle, setCustomTitle] = useState('')
  const [customMessage, setCustomMessage] = useState('')
  const [priority, setPriority] = useState('medium')
  const [isGenerating, setIsGenerating] = useState(false)
  const [batchCount, setBatchCount] = useState(1)
  
  const { generateTestNotification } = useNotificationStore()

  const testTypes = [
    {
      id: 'success',
      label: 'Success',
      icon: CheckCircle,
      color: 'text-green-600 bg-green-50 border-green-200',
      description: 'Positive confirmation messages'
    },
    {
      id: 'error',
      label: 'Error',
      icon: AlertCircle,
      color: 'text-red-600 bg-red-50 border-red-200',
      description: 'Critical error notifications'
    },
    {
      id: 'warning',
      label: 'Warning',
      icon: AlertTriangle,
      color: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      description: 'Important warnings and alerts'
    },
    {
      id: 'info',
      label: 'Information',
      icon: Info,
      color: 'text-blue-600 bg-blue-50 border-blue-200',
      description: 'General information updates'
    }
  ]

  const priorityLevels = [
    { id: 'low', label: 'Low', color: 'bg-gray-100 text-gray-700' },
    { id: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-700' },
    { id: 'high', label: 'High', color: 'bg-orange-100 text-orange-700' },
    { id: 'critical', label: 'Critical', color: 'bg-red-100 text-red-700' }
  ]

  const predefinedTests = [
    {
      title: 'System Maintenance',
      message: 'Scheduled maintenance will begin in 30 minutes',
      type: 'warning',
      priority: 'high'
    },
    {
      title: 'Backup Complete',
      message: 'Daily backup completed successfully at 2:30 AM',
      type: 'success',
      priority: 'low'
    },
    {
      title: 'Database Connection Error',
      message: 'Unable to establish connection to primary database',
      type: 'error',
      priority: 'critical'
    },
    {
      title: 'New Feature Available',
      message: 'Check out the new notification center features',
      type: 'info',
      priority: 'medium'
    }
  ]

  const handleGenerate = async (customTest = null) => {
    setIsGenerating(true)
    
    try {
      const testData = customTest || {
        type: testType,
        title: customTitle || getDefaultTitle(testType),
        message: customMessage || getDefaultMessage(testType),
        priority: priority
      }

      if (batchCount === 1) {
        await generateTestNotification(testData.type)
        toast.success(`${testData.type} notification generated!`)
      } else {
        // Generate multiple notifications with slight delays
        for (let i = 0; i < batchCount; i++) {
          setTimeout(async () => {
            await generateTestNotification(testData.type)
            if (i === 0) {
              toast.success(`Generating ${batchCount} notifications...`)
            }
          }, i * 500) // 500ms delay between each
        }
      }
      
      // Reset custom fields after generation
      setCustomTitle('')
      setCustomMessage('')
      
    } catch (error) {
      toast.error('Failed to generate test notification')
    } finally {
      setIsGenerating(false)
    }
  }

  const getDefaultTitle = (type) => {
    const titles = {
      success: 'Operation Successful',
      error: 'System Error',
      warning: 'Warning Alert',
      info: 'Information Update'
    }
    return titles[type] || 'Test Notification'
  }

  const getDefaultMessage = (type) => {
    const messages = {
      success: 'Your test operation completed successfully',
      error: 'A test error occurred in the system',
      warning: 'This is a test warning notification',
      info: 'Test information notification'
    }
    return messages[type] || 'This is a test notification'
  }

  const generateLoadTest = async () => {
    setIsGenerating(true)
    
    try {
      const types = ['success', 'error', 'warning', 'info']
      const promises = []
      
      // Generate 10 notifications of random types
      for (let i = 0; i < 10; i++) {
        const randomType = types[Math.floor(Math.random() * types.length)]
        promises.push(
          new Promise(resolve => {
            setTimeout(async () => {
              await generateTestNotification(randomType)
              resolve()
            }, i * 200) // Stagger by 200ms
          })
        )
      }
      
      await Promise.all(promises)
      toast.success('Load test completed! Generated 10 notifications')
      
    } catch (error) {
      toast.error('Load test failed')
    } finally {
      setIsGenerating(false)
    }
  }

  const selectedTypeInfo = testTypes.find(type => type.id === testType)

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <TestTube className="w-5 h-5 mr-2" />
          Test Notification Generator
        </h2>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Custom Test Generator */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium mb-4">Custom Test Notification</h3>
            
            {/* Notification Type Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notification Type
              </label>
              <div className="grid grid-cols-2 gap-3">
                {testTypes.map((type) => {
                  const Icon = type.icon
                  return (
                    <label
                      key={type.id}
                      className={`flex items-center space-x-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        testType === type.id
                          ? type.color
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="testType"
                        value={type.id}
                        checked={testType === type.id}
                        onChange={(e) => setTestType(e.target.value)}
                        className="sr-only"
                      />
                      <Icon className="w-5 h-5" />
                      <div>
                        <div className="font-medium">{type.label}</div>
                        <div className="text-xs opacity-75">{type.description}</div>
                      </div>
                    </label>
                  )
                })}
              </div>
            </div>

            {/* Priority Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority Level
              </label>
              <div className="flex space-x-2">
                {priorityLevels.map((level) => (
                  <label
                    key={level.id}
                    className={`px-3 py-2 rounded-lg border cursor-pointer transition-all ${
                      priority === level.id
                        ? `${level.color} border-current`
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="priority"
                      value={level.id}
                      checked={priority === level.id}
                      onChange={(e) => setPriority(e.target.value)}
                      className="sr-only"
                    />
                    <span className="text-sm font-medium">{level.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Custom Title and Message */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Title (optional)
              </label>
              <input
                type="text"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder={getDefaultTitle(testType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Message (optional)
              </label>
              <textarea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                placeholder={getDefaultMessage(testType)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Batch Count */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Notifications
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={batchCount}
                onChange={(e) => setBatchCount(Math.max(1, Math.min(10, parseInt(e.target.value) || 1)))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Generate 1-10 notifications at once</p>
            </div>

            {/* Generate Button */}
            <button
              onClick={() => handleGenerate()}
              disabled={isGenerating}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
              <span>{isGenerating ? 'Generating...' : 'Generate Test Notification'}</span>
            </button>
          </div>

          {/* Load Test */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium mb-4">Load Testing</h3>
            <p className="text-gray-600 mb-4">
              Generate multiple notifications quickly to test system performance and UI responsiveness.
            </p>
            <button
              onClick={generateLoadTest}
              disabled={isGenerating}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Zap className="w-4 h-4" />
              <span>{isGenerating ? 'Running Load Test...' : 'Run Load Test (10 notifications)'}</span>
            </button>
          </div>
        </div>

        {/* Predefined Tests */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Quick Test Templates</h3>
          {predefinedTests.map((test, index) => {
            const typeInfo = testTypes.find(t => t.id === test.type)
            const Icon = typeInfo?.icon || Info
            
            return (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 ${typeInfo?.color || 'text-gray-600 bg-gray-50 border-gray-200'}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <Icon className="w-5 h-5 mt-0.5" />
                    <div>
                      <h4 className="font-medium">{test.title}</h4>
                      <p className="text-sm opacity-75 mt-1">{test.message}</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <span className="text-xs px-2 py-1 bg-white/50 rounded capitalize">
                          {test.type}
                        </span>
                        <span className="text-xs px-2 py-1 bg-white/50 rounded capitalize">
                          {test.priority}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleGenerate(test)}
                    disabled={isGenerating}
                    className="px-3 py-1 text-xs bg-white hover:bg-gray-50 border border-current rounded transition-colors disabled:opacity-50"
                  >
                    Send
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default TestGenerator
