// 安全暴露有限的API给渲染进程
const { contextBridge } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    doSomething: () => { }
})