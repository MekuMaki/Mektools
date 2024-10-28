# Mektools-Version 1.0.1
## Mektools 1.0 for Dawntrail is finally here!

  ![MekTools Addon Interface](assets/mektools_1_0_1_ui.png)
 
 please wait a bit while I organize a proper tutorial and place it here...


 **Step 1:** Go to the green code button and hit Download ZIP (Do not unpack this)
 **Step 2:** Open Blender 4.2.2 or later
 **Step 3:** Go to Edit > Preferences > Addons > Install from disc...
 **Step 4:** Go to the N Panel in the 3D Viewport to the Mektools tab...

 Now you need to have something to import.

 Assuming you already have Dalamud installed along with Mare, Penumbra, Glamourer and other required plugins...

 Install [Meddle](https://github.com/PassiveModding/Meddle)

On the Meddle UI, go to the Options tab, change Export type to RAW. This will export raw textures that are used in the shaders from Skulblaka. Then go to the Character tab, select your character and hit Export All Models.

It will prompt you with a window to select where you will be exporting the models and textures, pick somewhere you will remember.

**Step 5:** Go to Mektools tab and hit "GLTF from Meddle"
**Step 6:** Navigate to your character.gltf that was exported (or whatever you named it)
**Step 7:** wait for a moment because it will make blender look like that its frozen-- it hasnt lol.

After you've hit this point, the character will be imported and processed according to how I typically set up characters in blender. All except for the shaders.

For the shaders to get fixed, you currently will need to do things a little manually still until a few things have been figured out...

The Append Shaders button will pull in the materials from the shaders.blend file, this is some shaders that all you need to do is replace the image textures with the ones that are for each part of your character. I plan to have this also be automated but that needs to come later when some color set stuff has been figured out.

**I will make a detailed video tutorial explaining how to import things and get gear to look proper too! just keep an eye out!**

The Rigs Male and Female buttons is used to manually append the Dawntrail Mekrigs to your scene. This is intended if you go to File > Import > GLTF or FBX and want to do things manually.

The button for Import GLTF from Meddle and FBX from Textools are both to set things up automatically.

Finally, Join the [Discord](https://www.discord.gg/98DqcKE) and ask any questions in the Help channel or share the cool stuff you've made with mektools!
If there are any issues found, please make sure you are using Blender 4.2 or higher and then send a message in the discord server for help.
