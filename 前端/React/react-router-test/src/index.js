import React from 'react';
import ReactDOM from 'react-dom';
// BrowserRouter处理服务器动态请求使用 HashRouter处理只有静态文件的服务器网站
import {BrowserRouter as Router,Route,Switch} from "react-router-dom";

import About from "./components/About"
import App from "./components/App"
import Repos from "./components/Repos"
import Repo from "./components/Repo"


ReactDOM.render(
    (
        <Router>
            <div>
                {/* Route 注册路由，path为路径 component为指向的组件*/}
                <Route path="/" component={App}/>
                {/* Switch 包裹多个<Route>，对子元素路由进行迭代，仅渲染一个*/}
                <Switch>
                    <Route path="/about" component={About}/>
                    {/* 注意这组件嵌套的用法*/}
                    <Repos> {/* 在这不能注册此组件的路由 否则，子组件内容不能显示 */}
                        {/* :name 为占位符写法，不确定参数值是什么*/}
                        <Route path="/repos/:name/:repo" component={Repo} />
                    </Repos>
                </Switch>
            </div>
        </Router>
    ),
    document.getElementById("root")
);