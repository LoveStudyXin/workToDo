/**
 * 前端测试报告生成器
 * 运行方式: cd frontend && npx ts-node src/generate-report.ts
 * 或: cd frontend && npx vitest run --reporter=json > test-results.json
 */

// 测试用例定义
export const FRONTEND_TEST_CASES = {
  "Auth Store（认证状态管理）": [
    { name: "用户初始为空", description: "验证未登录时用户信息为空" },
    { name: "未登录时 isAuthenticated 为 false", description: "验证未登录状态判断正确" },
    { name: "登录成功后保存 token", description: "验证登录后 token 正确存储到 localStorage" },
    { name: "登录成功后获取用户信息", description: "验证登录后自动获取并保存用户信息" },
    { name: "注册调用正确的 API", description: "验证注册功能调用正确的接口" },
    { name: "登出后清除用户信息和 token", description: "验证登出后清理所有认证状态" },
  ],
  "Todo Store（任务状态管理）": [
    { name: "任务列表初始为空", description: "验证初始化时任务列表为空数组" },
    { name: "loading 初始为 false", description: "验证初始加载状态为 false" },
    { name: "fetchTodos 获取所有任务", description: "验证能正确获取任务列表" },
    { name: "fetchTodos 支持筛选条件", description: "验证支持按状态等条件筛选任务" },
    { name: "fetchTodayTodos 获取今日任务", description: "验证能获取今日待办任务" },
    { name: "加载时 loading 为 true", description: "验证请求中 loading 状态正确" },
    { name: "createTodo 创建新任务", description: "验证创建任务后添加到列表开头" },
    { name: "updateTodo 更新任务", description: "验证更新任务后列表同步更新" },
    { name: "deleteTodo 删除任务", description: "验证删除任务后从列表移除" },
  ],
  "Login（登录逻辑）": [
    { name: "空表单提交时显示提示", description: "验证空表单提交时显示错误提示" },
    { name: "登录成功后调用正确的方法", description: "验证登录成功后保存token并跳转首页" },
    { name: "登录失败时显示错误信息", description: "验证登录失败时显示后端返回的错误信息" },
  ]
}

console.log("前端测试用例汇总：")
console.log("==================")
let total = 0
for (const [module, tests] of Object.entries(FRONTEND_TEST_CASES)) {
  console.log(`\n${module}（${tests.length}个）:`)
  tests.forEach((t, i) => {
    console.log(`  ${i + 1}. ${t.name}`)
    console.log(`     ${t.description}`)
  })
  total += tests.length
}
console.log(`\n总计: ${total} 个测试用例`)
