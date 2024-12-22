from env_rob_train import ROSEnv
import os
from stable_baselines3 import PPO
import datetime
from time import time
import yaml
from stable_baselines3.common.evaluation import evaluate_policy

def train(n_cubos_max: int = 2, visualization:bool = False, save_data:bool = False, verbose:bool = False):
    path = f"./src/proyecto_final/scripts/rl/logs/{n_cubos_max}_cubos"
    try:
        os.mkdir(path)
    except:
        pass
    env = ROSEnv(num_cubos_max=n_cubos_max, visualization=visualization, save_data=save_data, verbose=verbose)
    env.reset()

    ini_time = time()

    default_parameters = {'policy': 'MlpPolicy',
                            'env' : env,
                            'learning_rate': 3e-4,
                            'n_steps' : 2048,
                            'batch_size' : 64,
                            'n_epochs' : 10,
                            'gamma':  0.99,
                            'gae_lambda':  0.95,
                            'clip_range': 0.2,
                            'clip_range_vf' : None,
                            'normalize_advantage': True,
                            'ent_coef': 0.0,
                            'vf_coef': 0.5,
                            'max_grad_norm': 0.5,
                            'use_sde': False,
                            'sde_sample_freq': -1,
                            'target_kl': None,
                            'tensorboard_log': path,
                            'policy_kwargs': None,
                            'verbose': 1,
                            'seed': None,
                            'device': "auto"
                            }

    parameters = {'policy': 'MlpPolicy',
                    'env' : env,
                    'learning_rate': 3e-4,
                    'n_steps' : 2048,
                    'batch_size' : 64,
                    'n_epochs' : 10,
                    'gamma':  0.99,
                    'gae_lambda':  0.95,
                    'clip_range': 0.2,
                    'clip_range_vf' : None,
                    'normalize_advantage': True,
                    'ent_coef': 0.0,
                    'vf_coef': 0.5,
                    'max_grad_norm': 0.5,
                    'use_sde': False,
                    'sde_sample_freq': -1,
                    'target_kl': None,
                    'tensorboard_log': path,
                    'policy_kwargs': None,
                    'verbose': 1,
                    'seed': None,
                    'device': "auto"
                    }


    model = PPO(**parameters)
    model.__module__
    
    today = datetime.datetime.now()
    date = f'{today.year}_{today.month}_{today.day}_{today.hour}_{today.minute}'
    tb_log_name = f'PPO_{date}_cubes_{n_cubos_max}'
    total_timesteps = 20

    model.learn(total_timesteps=total_timesteps, log_interval=5, tb_log_name=tb_log_name)

    end_time = time()
    
    mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

    obs, _ = env.reset()
    action, _ = model.predict(obs)
    _, _, _, info = env.step(action)

    model_path = f"src/proyecto_final/scripts/rl/agentes_entrenados/ppo_rosenv_{date}_cubes_{n_cubos_max}"

    parameters.pop('env')

    # Crear una estructura jerárquica para las secciones
    save_in_yaml = {'Agente' : {
        'Agent_Info': {
            'Agent_name': model_path,
            'Log_name': tb_log_name,
            'date': date},
        'Train_Info' : {
            'model' : model.__module__,
            'total_timesteps': total_timesteps,
            'train_time': end_time - ini_time,
            'mean_reward': float(mean_reward),
            'std_reward': float(std_reward),
            'cubos': n_cubos_max
        },
        'Success_Rates' : info,
        'Agent_Parameters': parameters,
        'Comentario' : 'Introduce Comentario'
    }}

    model.save(model_path)
    with open('src/proyecto_final/scripts/rl/yaml_logs/logs_entrenamientos', '+a') as f:
            yaml.dump(save_in_yaml, f, default_flow_style=False, sort_keys=False)

def test(n_cubos_max:int = 2, seed:int = None):
    env = ROSEnv(n_cubos_max, visualization=True, seed=seed)

    model = PPO.load('src/proyecto_final/scripts/rl/agentes_entrenados/ppo_rosenv_2024_12_8_23_38_cubes_2.zip')

    while True:
        obs, _ = env.reset(seed=seed)
        action, _ = model.predict(obs)
        _, _, _, _ = env.step(action)

        choice = input('Continuar? (q para salir)')
        if choice == 'q':
            break

if __name__ == '__main__':
    n_cubos_max = 2
    prueba = False
    if not prueba:   
        train(n_cubos_max=2, visualization=True, save_data=False, verbose=True)
    else:
        test(n_cubos_max=n_cubos_max, seed=2)