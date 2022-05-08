"""defines the Poll-Class which represents the Poll-object"""

import disnake
from disnake.channel import TextChannel, Thread
from disnake.message import Message

from asyncio import sleep


class Poll(object):
    """Represents the Poll-Object which the Bot can create.
    Attributes
    -----------
    poll_name: :class:`str`
        The display-name of the poll.
    time: :class:`int`
        The lasting time of the poll.
    ans_number: :class:`int`
        The number of answers the poll consits of.
    answer_options: :class:`list[AnswerOption]`
        The list of all answer options of the poll.
    mess: :class:`Message`
        The message, wich currently displays the poll in the TextChannel.
        Is ``None`` when there wasn't sent a message yet.
    emojis: :class:`list[str]`
        The default emoji list which stores the emojis representing
        the answer options of the poll.
    channel: :class:`TextChannel | Thread`
        The Discord text-channel or Thread the poll belongs to.
    """

    def __init__(self, channel, ans_number = 0, time = 60, name = 'default'):
        self.poll_name: str = name
        self.time: int = time
        self.ans_number: int = ans_number
        self.answer_options: list[AnswerOption] = []
        self.mess: Message = None
        self.emojis: list[str] = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        self.channel: TextChannel | Thread = channel

        for i in range(ans_number):
            self.answer_options.append(AnswerOption(f"default_option {i}"))

    async def new_ans_op(self, name: str):
        """adds a new `AnswerOption`into the answer_options list"""

        if self.ans_number == 11:
            raise PollError(f"Could not add '{name}'. Maximum number of answer options reached.")

        self.answer_options.append(AnswerOption(name))
        self.ans_number += 1

    async def del_ans_op(self, index: int):
        """deletes an answer option by list-index"""
        try:
            removed = self.answer_options.pop(index)
        except IndexError:
            raise PollError("Answer could not be deleted from answer_options (doesn't exist)")
         
        await self.channel.send(f"Removed '{removed}'")
        self.ans_number -= 1
        
    async def send_setup_Embed(self):
        """sends a new setup message (as Embed) in the Text-Channel and deletes the last setup Message,
        if this isn't the first one"""
        
        embed = disnake.Embed(title=self.poll_name, colour=disnake.Colour(0xc9a881),
                            description=f"\n**Current Settings:**\npoll name = '{self.poll_name}'\ntime = {self.time} seconds\nnumber of answers = {self.ans_number}\n\n**Current answer oprions:**\n",
                            timestamp=datetime.datetime.now())

        for i in range(self.ans_number):
            embed.add_field(name=self.emojis[i], value=self.answer_options[i].name, inline=True)

        if self.mess != None:
            await self.mess.delete()
        self.mess = await self.channel.send(embed=embed)


    async def start(self):
        """Starts the poll-Event. If the poll lasts longer than 24 hours (and poll is in Thread) then it sends a message every 24 hours in the Thread
        to prevent the Thread from auto-archiving."""

        if self.ans_number < 2:
            raise PollError("Cannot start poll with less than 2 answer options.")

        await self.send_progress_Embed()

        if type(self.channel) is Thread:
            while(self.time > 86400):
                self.time -= 86400
                await sleep(86400)
                print("send Auto dearchive message")
                message = await self.channel.send("Auto-dearchive message.")
                await message.delete()
        await sleep(self.time)

    async def send_progress_Embed(self):
        """sends a new message (as Embed) which is shown while the poll is in progress, replaces and deletes current self.mess"""
        
        time = datetime.datetime.now() + datetime.timedelta(seconds=float(self.time))
        time = str(time)
        time = time.split(".")[0]
        embed = disnake.Embed(title=self.poll_name, colour=disnake.Colour(0xc9a881),
                            description = f"Active Poll:\n\nReact with one of the given Emoji's to vote. The poll will end at {time}.\n\n**Answer Options are:**\n",
                            timestamp=datetime.datetime.now())

        for i in range(self.ans_number):
            embed.add_field(name=self.emojis[i], value=self.answer_options[i].name, inline=True)
        
        await self.mess.delete()
        self.mess = await self.channel.send(embed=embed)

        for i in range(self.ans_number):
            await self.mess.add_reaction(self.emojis[i])

    async def analyze_results(self, message: Message):
        """checks which answer option has won the poll"""

        maxvotes = -1
        winner = -1

        for i in range(len(message.reactions)):
            for j in range(self.ans_number):
                if message.reactions[i].emoji == self.emojis[j]:
                    self.answer_options[j].votes = message.reactions[i].count
        
        for i in range(self.ans_number):
            if self.answer_options[i].votes > maxvotes:
                maxvotes = self.answer_options[i].votes
                winner = i

        await self.send_result_Embed(winner)

    async def send_result_Embed(self, winner: int):
        """sends a new result-message (as Embed) which is shown after the poll-event ends also replaces and deletes the current self.mess, archives the Thread if 
        the poll is in a Thread"""
        
        embed = disnake.Embed(title=self.poll_name, colour=disnake.Colour(0xc9a881),
                            description= f"**The Winner is drawn**\n\n{self.answer_options[winner].name} has won the poll with {self.answer_options[winner].votes-1} votes.",
                            timestamp=datetime.datetime.now())

        await self.mess.delete()
        self.mess = await self.channel.send(embed=embed)
        if type(self.channel) is Thread:
            await self.channel.edit(archived=True)

class AnswerOption:
    """Represents an answer option in an Poll Object.
    
    Attributes
    -----------
    name: :class:`str`
        The String representing the answer option.
    time: :class:`int`
        Number of votes on this Option."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.votes: int = 0

    def __str__(self) -> str:
        return self.name

class PollError(Exception):
    """Custom Exception for all Exeptions raised in the Poll-Class"""

    def __init__(self, error: str) -> None:
        self.error_message = error

    def __str__(self) -> str:
        return self.