from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)

def reply_message(result, event, line_bot_api):
    if result == -1:
        reply1 = "商品不存在日本Uniqlo哦! (期間限定價格商品可能找不到)"
        reply2 = "請重新輸入或按 1 看範例~"
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
            replyToken=event.reply_token, 
            messages=[TextMessage(text=reply1),
                        TextMessage(text=reply2)]))
    else:
        reply1 = "商品連結:\n %s\n商品價格: %s日圓\n折合台幣: %s元" % (result[1], result[2], result[3])
        # reply1 = "商品連結:\n %s\n商品價格: %s日圓\n折合台幣: %s元\n臺灣官網售價: %s元" % (result[1], result[2], result[3], result[4][2])
        if len(result[4]) != 0:
            try:
                reply1 += "\n臺灣官網售價: {}元".format(result[4][2])
            except:
                reply1 += "\n臺灣官網售價: {}元".format(result[4][1])
        available_dict = {}
        if len(result) == 6:
            for item in result[5]:
                if item['stock'] != 'STOCK_OUT' and item['color'] not in available_dict:
                    available_dict[item['color']] = []
                if item['stock'] != 'STOCK_OUT' and item['color'] in available_dict:
                    available_dict[item['color']].append(item['size'])

            reply2 = "日本官網庫存:"
            for color in available_dict:
                reply2 += "\n{}: ".format(color)
                reply2 += "{}".format(', '.join(available_dict[color]))
        else:
            reply2 = "日本官網庫存查不到"

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
            replyToken=event.reply_token, 
            messages=[TextMessage(text=reply1),
                        TextMessage(text=reply2)]))