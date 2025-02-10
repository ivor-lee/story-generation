from metagpt.llm import LLM
import asyncio

async def test_llm_connection():
    try:
        llm = LLM()
        response = await llm.aask("你好，请告诉我今天是星期几？")
        print("LLM 连接测试成功！")
        print("回复内容:", response)
        return True
    except Exception as e:
        print("LLM 连接测试失败！")
        print("错误信息:", str(e))
        return False

if __name__ == "__main__":
    asyncio.run(test_llm_connection())