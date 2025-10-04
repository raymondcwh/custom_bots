Made for specific automation tasks by running cron jobs in background, with notifications in Telegram channels.

Use following command:
'* * * * * python script_path"
With conda env,
'* * * * * /bin/bash -c "source filepath_for_conda.sh && conda activate env_name && python script_path && conda deactivate"'