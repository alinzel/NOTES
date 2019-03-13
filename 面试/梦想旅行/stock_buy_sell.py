
'''
    假设有一只股票，在过去的一天里，观察到的一组价格分别是 6,3,9,2,5,9,1,4,6 
    写一段程序，计算出什么时候买进，什么时候卖出收益最大
'''
price_list = [6,3,9,2,5,9,1,4,6]


def stock(price_list):
    max_earn = 0
    buy = 0
    sell = 0
    length = len(price_list)

    for buy_index, buy_item in enumerate(price_list):
        for sell_index in range(buy_index+1, length):
            earn = price_list[sell_index] - buy_item
            if earn > max_earn:
                max_earn = earn
                buy = buy_index
                sell = sell_index

    return buy,sell,max_earn

buy,sell,max_earn = stock(price_list)

print(buy,sell,max_earn)