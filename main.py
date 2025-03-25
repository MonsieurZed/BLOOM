import script.basic as basic
import script.gpt as gpt
import script.foocus as foocus

quantity = 1
name = "25SEPT94"
story = """
25 Septembre 1994
Cette année-là, un étudiant se déguisa en Dracula pour Halloween. 
Sa touche finale : une planche de pin sous son t-shirt, au niveau du torse, pour qu'il puisse planter un couteau dans la planche de façon trés réaliste et prétendre qu'il était transpercé par un pieu mortel.
Il oublia de prendre en compte la résistance de la fine planche quand il a planté le couteau avec un marteau. Propulsée par ce dernier, la pointe bien affûtée du couteau a coupé la planche en deux et est entrée dans son coeur.
Il entra dans la fête en chancelant, et dit "Je l'ai vraiment fait !" avant de s'effondrer devant ses amis horrifiés.
"""

basic.checks()
gpt.generate_scripts(name, story)
foocus.generate_images_from_prompts(name, quantity)
