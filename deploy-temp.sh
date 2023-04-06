echo -e "Deploying temp temp_plugin ..."
start="$(date +%s)"

rm -rf ~/Library/Application\ Support/Blender/3.3/scripts/addons/temp_plugin
mkdir ~/Library/Application\ Support/Blender/3.3/scripts/addons/temp_plugin
cp -r ./temp_plugin ~/Library/Application\ Support/Blender/3.3/scripts/addons
/Applications/Blender.app/Contents/MacOS/Blender -b -P ~/Library/Application\ Support/Blender/3.3/scripts/addons/temp_plugin/deploy-plugin.py

runtime=$[ $(date +%s) - $start ]
echo -e "\033[0;32mDeployed successfully in ${runtime} second(s)!\033[0m"

