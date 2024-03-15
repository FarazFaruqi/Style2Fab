echo -e "Deploying plugin ..."
start="$(date +%s)"

rm -rf ~/Library/Application\ Support/Blender/3.3/scripts/addons/plugin
mkdir ~/Library/Application\ Support/Blender/3.3/scripts/addons/plugin
cp -r ./plugin ~/Library/Application\ Support/Blender/3.3/scripts/addons
/Applications/Blender.app/Contents/MacOS/Blender -b -P ~/Library/Application\ Support/Blender/3.3/scripts/addons/plugin/deploy-plugin.py

runtime=$[ $(date +%s) - $start ]
echo -e "\033[0;32mDeployed successfully in ${runtime} second(s)!\033[0m"

