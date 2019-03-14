import React from "react"
import {Link} from "react-router-dom";

class Repos extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            repos:[
                {name:"google",repo:"github"},
                {name:"antd",repo:"antd"},
                {name:"facebook",repo:"react" }
            ]
        }
    }
    render() {
        let {repos} = this.state;
        return(
            <div>
                <h2>Repos组件...</h2>
                <ul>
                    {repos.map((item,index)=>{
                        return <li key={index}><Link to={`/repos/${item.name}/${item.repo}`}>{item.repo}</Link></li>
                    })}
                </ul>
                {/*显示子路由组件的数据内容*/}
                {this.props.children}
            </div>
        )
    }
}

export default Repos