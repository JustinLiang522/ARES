appium_port=4723
apps=("diary-1" "diary-2" "diary-3" "diary-4" "diary-5")
udid="10.92.81.101:35453"
host="10.92.83.4"

for app in "${apps[@]}"; do # iterate through the list of apps
    python -m rl_interaction.test_application --real_device --algo SAC --appium_port $appium_port --timesteps 4000 --iterations 1 --udid $udid --host $host --android_port 45591 --device_name "samsung" --apps rl_interaction/apps/$app.apk --max_timesteps 250 --pool_strings rl_interaction/strings.txt --timer 180 --platform_version 11.0 --trials_per_app 1 --menu
done
