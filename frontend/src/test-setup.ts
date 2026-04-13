// 测试环境设置
// Mock CSS imports
import { vi } from 'vitest'

// 忽略所有 CSS 文件
vi.mock('*.css', () => ({}))
