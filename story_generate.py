from metagpt.roles import Role
from metagpt.schema import Message
from typing import Dict, List
from metagpt.actions import Action
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class StoryGenerator(Role):
    def __init__(self):
        super().__init__(
            name="StoryGenerator", 
            profile="A creative story generator",
            actions=[GenerateStoryAction(), EditStoryAction()]
        )
        self.story_parameters: Dict = {}

    async def generate_outline(self, theme: str, characters: List[Dict], setting: str) -> str:
        # 使用 GenerateStoryAction 来生成故事
        action = next(action for action in self.actions if isinstance(action, GenerateStoryAction))
        story = await action.run(theme, characters, setting)
        return story

class GenerateStoryAction(Action):
    def __init__(self):
        super().__init__()
        self.name = "GenerateStoryAction"
        
    async def run(self, theme: str, characters: List[Dict], setting: str):
        try:
            prompt = self._generate_prompt(theme, characters, setting)
            return await self.llm.aask(prompt)
        except Exception as e:
            logger.error(f"Error in GenerateStoryAction: {str(e)}")
            raise
            
    def _generate_prompt(self, theme: str, characters: List[Dict], setting: str) -> str:
        return f"""
        请基于以下参数生成一个完整的故事：
        
        主题：{theme}
        角色：{characters}
        设定：{setting}
        
        请提供：
        1. 故事梗概
        2. 主要情节发展
        3. 关键转折点
        4. 结局
        
        请用流畅的叙事方式呈现故事。
        """

class EditStoryAction(Action):
    def __init__(self):
        super().__init__()
        self.name = "EditStoryAction"
        
    async def run(self, story_content: str, edit_instructions: str):
        try:
            prompt = f"请根据以下指示修改故事：\n原故事：{story_content}\n修改要求：{edit_instructions}"
            return await self.llm.aask(prompt)
        except Exception as e:
            logger.error(f"Error in EditStoryAction: {str(e)}")
            raise

class StoryRequest(BaseModel):
    theme: str
    characters: List[Dict]
    setting: str

@app.post("/generate_story")
async def generate_story(request: StoryRequest):
    try:
        generator = StoryGenerator()
        story = await generator.generate_outline(
            request.theme,
            request.characters,
            request.setting
        )
        return {"story": story}
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/edit_story")
async def edit_story(story_content: str, edit_instructions: str):
    try:
        editor = EditStoryAction()
        edited_story = await editor.run(story_content, edit_instructions)
        return {"edited_story": edited_story}
    except Exception as e:
        logger.error(f"Error editing story: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
