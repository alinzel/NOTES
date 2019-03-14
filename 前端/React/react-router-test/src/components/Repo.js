import React from "react"

class Repo extends React.Component{
    render() {
        return(
            <div>
                {/* 获取路由中的参数 props.match.params.占位符名字*/}
                公司：{this.props.match.params.name} 产品：{this.props.match.params.repo}
            </div>
        )
    }
}

export default Repo