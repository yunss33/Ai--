import pyttsx3

engine = pyttsx3.init()  # 初始化引擎
engine.setProperty('rate', 150)  # 语速（默认200）
engine.setProperty('volume', 0.8)  # 音量（0-1）

# 选择语音（需系统有多个语音包）
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0为默认，1可能是女声（依系统而定）

engine.say("Hello, 这是离线TTS示例, 你好, 我是小助手")  # 文本内容
engine.runAndWait()  # 执行并等待完成
#engine.save_to_file("保存为音频文件", "output.mp3")  # 保存到本地
engine.runAndWait()