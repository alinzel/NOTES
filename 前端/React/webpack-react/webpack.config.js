const path = require('path'); //path内置的模块，用来设置路径。

module.exports = {
    entry: './src/js/main.js',   // 入口文件路径
    output: {                     // 输出配置
        filename: 'bundle.js',      // 输出文件名
        path: path.resolve(__dirname, 'dist')   //输出文件路径配置
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            },
            //babel处理js
            {
                test: /\.js$/,
                exclude: /node_modules/, //排除此文件夹
                use: [
                    'babel-loader'
                ]
            }

        ]
    },
    devServer:{ contentBase: './'} ,//热部署配置，两个必要条件，根目录寻找，必须index文件
};