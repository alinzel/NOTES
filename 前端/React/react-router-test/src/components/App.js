import React from "react"
import {Link} from "react-router-dom"


class App extends React.Component{
    render() {
        return(
            <div>
                <h2>App组件...</h2>
                <ul>
                    <li>
                        {/*Link 生成a标签 属性to指向已经注册的路由*/}
                        <Link to="/about">about</Link>
                    </li>
                    <li>
                        <Link to="/repos">repos</Link>
                    </li>
                </ul>
                <hr/>
                {/*显示子路由组件的数据内容*/}
                {this.props.children}
            </div>
        )
    }
}

export default App