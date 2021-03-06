import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict
import os
import sys
sys.path.append('/home/mldp/ML_with_bigdata')
import data_utility as du
import CNN_RNN.utility

root_dir = '/home/mldp/ML_with_bigdata'
logger = CNN_RNN.utility.setlog('analysize')


def analysis_energy_effi():
	'''
	not in use anymore
	'''
	def get_energyEFFI_pd(file_path):
		data_array = du.load_array(file_path)
		energy_array = data_array[:, -149:, 2]  # (144, 1486)
		cell_num_array = data_array[:, 0, 0]

		energy_array = np.mean(energy_array, axis=1)  # 144
		data_array = np.stack((cell_num_array, energy_array), axis=-1)
		df = pd.DataFrame({
			'EE': data_array[:, 1],
			'cell_num': [int(cell_num) for cell_num in data_array[:, 0]]})
		df = df.set_index('cell_num')
		# print(df.describe())

		return df

	def plot_KDE(data_frame, title):
		# data_frame = data_frame[['ARIMA(STL)', 'LM(STL)', 'RNN(MTL)', '3D CNN(MTL)', 'CNN-RNN(*)', 'CNN-RNN(STL)', 'CNN-RNN(MTL)']]
		ax = data_frame.plot(kind='kde', title=title + ' KDE plot')
		# ax.set_xlabel('Energy efficiency')
		# ax.set_xlim(0, 0.09)
		ax.legend(loc='upper left', fontsize='large')

	def grouping_by_macro_load(EFFI_df):
		# load_groups_list = get_groups_load_list()
		# print(EFFI_df.describe())
		without_loading_data_path = os.path.join(root_dir, 'offloading/result/without_offloading_without_RL', 'all_cell_result_array_0731.npy')
		cell_result = du.load_array(without_loading_data_path)
		# cell_result = cell_result[:, :]
		macro_load_array = cell_result[:, -149:, 4]  # (144, 149)
		macro_load_array_mean = np.mean(macro_load_array, axis=1)
		macro_load_array = cell_result[:, :, 4]  # (144, 1486)
		macro_cell_num = cell_result[:, 0, 0]
		macro_load_pd = pd.DataFrame({
			'cell_num': [int(cell_num) for cell_num in macro_cell_num],
			'macro_load': macro_load_array_mean})
		macro_load_pd = macro_load_pd.set_index('cell_num')
		# print(macro_load_pd)

		EFFI_df = pd.concat((EFFI_df, macro_load_pd), axis=1)
		bins = (0, 0.3, 0.7, 1, 2, 10)
		cats_macro_load_pd = pd.cut(EFFI_df['macro_load'], bins)
		EFFI_df_group_by_macro_load = EFFI_df.groupby(cats_macro_load_pd)
		key_list = list(EFFI_df_group_by_macro_load.groups.keys())
		key_list = sorted(key_list, key=lambda x: x)
		# print(EFFI_df_group_by_macro_load.get_group(key_list[0]))
		# print(key_list)
		logger.info('\n{}'.format(EFFI_df_group_by_macro_load.count()))
		logger.info('\n{}'.format(EFFI_df_group_by_macro_load.mean()))
		# for group in EFFI_df_group_by_macro_load:
		# 	print(group[1].head(3))
		return key_list, EFFI_df_group_by_macro_load

	prediction_offloading_RL_path = os.path.join(root_dir, 'offloading/result/with_preidction_with_RL', 'all_cell_result_array_0731.npy')
	without_offloading_RL_path = os.path.join(root_dir, 'offloading/result/without_offloading_without_RL', 'all_cell_result_array_0731.npy')
	offloading_without_RL_path = os.path.join(root_dir, 'offloading/result/offloading_without_RL', 'all_cell_result_array_0731.npy')
	God_prediction_offload_RL_path = os.path.join(root_dir, 'offloading/result/RL_with_god_prediction', 'all_cell_result_array.npy')
	offloading_RL_without_prediction_path = os.path.join(root_dir, 'offloading/result/RL_without_prediction', 'all_cell_result_array_0726.npy')
	_10mins_offloading_RL_without_prediction_path = os.path.join(root_dir, 'offloading/result/RL_10mins_without_prediction', 'all_cell_result_array_0731.npy')
	offloading_q_table_path = os.path.join(root_dir, 'offloading/result/with_Q_table_without_prediction', 'all_cell_result_array_0927.npy')

	prediction_offloading_RL = get_energyEFFI_pd(prediction_offloading_RL_path)
	without_offloading_RL = get_energyEFFI_pd(without_offloading_RL_path)
	offloading_without_RL = get_energyEFFI_pd(offloading_without_RL_path)

	God_prediction_offload_RL = get_energyEFFI_pd(God_prediction_offload_RL_path)
	offloading_RL_without_prediction = get_energyEFFI_pd(offloading_RL_without_prediction_path)
	_10mins_offloading_RL_without_prediction = get_energyEFFI_pd(_10mins_offloading_RL_without_prediction_path)
	offloading_with_Q_table = get_energyEFFI_pd(offloading_q_table_path)

	EFFI_df = pd.concat((
		prediction_offloading_RL, without_offloading_RL, offloading_without_RL, _10mins_offloading_RL_without_prediction, offloading_with_Q_table),
		axis=1)
	EFFI_df.columns = ['Pre_off_RL', 'without_off_RL', 'off_without_RL', '10_mins_without_pre', 'off_Qtable']
	# df = EFFI_df[EFFI_df < 0].dropna()
	logger.info('\n {}'.format(EFFI_df.describe()))
	# EFFI_df.plot(kind='hist', subplots=True)
	# plot_KDE(EFFI_df, 'Energy efficiency')
	# plt.show()
	grouping_by_macro_load(EFFI_df[['without_off_RL', 'off_without_RL', 'Pre_off_RL', '10_mins_without_pre', 'off_Qtable']])


def get_dataframe(file_path):
	data_array = du.load_array(file_path)
	data_array = data_array[:, -149:]

	cell_num_array = data_array[:, 0, 0]
	reward_array = np.mean(data_array[:, :, 1], axis=1)
	energy_array = np.mean(data_array[:, :, 2], axis=1)
	traffic_digested_array = np.sum(data_array[:, :, 3], axis=1)
	macro_load_array = np.mean(data_array[:, :, 4], axis=1)
	small_load_array = data_array[:, :, 5]
	small_load_array[small_load_array == 0] = np.nan
	small_load_array = np.nanmean(small_load_array, axis=1)
	power_consumption_array = np.sum(data_array[:, :, 6], axis=1)
	action_array = np.mean(data_array[:, :, 7], axis=1)
	traffic_demand_array = np.sum(data_array[:, :, 8], axis=1)  # sum of data within 149
	df = pd.DataFrame({
		'cell_num': [int(cell_num) for cell_num in cell_num_array[:]],
		'reward': reward_array,
		'energy efficiency': energy_array,
		'traffic digested': traffic_digested_array,
		'macro load': macro_load_array,
		'small load': small_load_array,
		'power consumption': power_consumption_array,
		'small cell number': action_array,
		'traffic demand': traffic_demand_array})

	df = df.set_index('cell_num')
	return df


def grouping_by_macro_load(df):
	without_loading_data_path = os.path.join(root_dir, 'offloading/result/without_offloading_without_RL', 'all_cell_result_array_0731.npy')
	cell_result = du.load_array(without_loading_data_path)
	macro_load_array = cell_result[:, -149:, 4]  # (144, 1486)  # according 149
	macro_load_array_mean = np.mean(macro_load_array, axis=1)
	macro_load_array = cell_result[:, :, 4]  # (144, 1486)
	macro_cell_num = cell_result[:, 0, 0]
	macro_load_pd = pd.DataFrame({
		'cell_num': [int(cell_num) for cell_num in macro_cell_num],
		'base_macro_load': macro_load_array_mean})
	macro_load_pd = macro_load_pd.set_index('cell_num')

	df = pd.concat((df, macro_load_pd), axis=1)
	bins = (0, 0.3, 0.7, 1, 2, 10)
	# bins = (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 2, 3, 10)
	cats_macro_load_pd = pd.cut(df['base_macro_load'], bins)
	df_group = df.groupby(cats_macro_load_pd)
	logger.debug('macro load group count:{}'.format(df_group.count()))
	key_list = list(df_group.groups.keys())
	key_list = sorted(key_list, key=lambda x: x)

	return key_list, df_group


def get_groups_load_dict():
	'''
	group each cells load into different level
	'''
	without_loading_data_path = os.path.join(root_dir, 'offloading/result/without_offloading_without_RL', 'all_cell_result_array_0731.npy')
	cell_result = du.load_array(without_loading_data_path)
	logger.debug('cell result shape:{}'.format(cell_result.shape))  # (144, 1486, 8) 144: cell_num, 1486: time sequence, 8:cell_num, reward, energy, traffic_demand, macro load, small load, power consumption
	macro_load_array = cell_result[:, -149:, 4]  # (144, 149)
	macro_load_array_mean = np.mean(macro_load_array, axis=1)

	macro_cell_num = cell_result[:, 0, 0]

	macro_load_pd = pd.DataFrame({
		'cell_num': macro_cell_num,
		'macro_load': macro_load_array_mean})
	# print(macro_load_pd)
	bins = (0, 0.3, 0.7, 1, 2, 10)
	cats_macro_load_pd = pd.cut(macro_load_pd['macro_load'], bins)
	# print(cats_macro_load_pd)
	macro_load_pd_group = macro_load_pd.groupby(cats_macro_load_pd)
	load_groups_dict = OrderedDict()
	for index, group in enumerate(macro_load_pd_group):
		# print(group[1]['cell_num'])
		group_list = [cell_num for cell_num in group[1]['cell_num']]
		# print(group_list)
		load_groups_dict[group[0]] = group_list
		# load_group_dict[group[0]] = group[1]['cell_num']
	# print(macro_load_pd_group.count())
	# for key, v in load_group_dict.items():
	return load_groups_dict


def get_column_method(method_dict, column_name):
	new_dict = OrderedDict()
	for key, method in method_dict.items():
		df = method[column_name]
		df.name = key
		new_dict[key] = df

	return new_dict


def get_column_data_frame(method_dict, column_name):
	method_dict = get_column_method(method_dict, column_name)
	df = pd.DataFrame()
	for key, method in method_dict.items():
		df = pd.concat((df, method), axis=1)
	return df


def analysis_low_load(method_dict):
	def get_low_load_group(method_dict):
		for key, method in method_dict.items():
			key_list, df_group = grouping_by_macro_load(method)
			logger.debug('low load, key:{}'.format(key_list[0]))
			method_dict[key] = df_group.get_group(key_list[0])
		return method_dict

	def energy_effi(energy_effi_dict):
		energy_effi_df = pd.DataFrame()
		for key, method in energy_effi_dict.items():
			# print(key)
			# print(method.describe())
			# print(method)
			energy_effi_df = pd.concat((energy_effi_df, method), axis=1)

		energy_effi_mean_df = energy_effi_df.mean()
		ax = energy_effi_mean_df.plot(kind='bar', alpha=0.7, rot=45, width=0.2, color=['red', 'green', 'blue', 'cyan', 'magenta'])

	method_dict = get_low_load_group(method_dict)
	energy_effi_dict = get_column_method(method_dict, 'energy efficiency')

	energy_effi(energy_effi_dict)


def analysis_origin_macro_load_group(method_dict):
	traffic_demand_df = get_column_data_frame(method_dict, 'traffic demand')['Without offloading']
	origin_macro_load_df = get_column_data_frame(method_dict, 'macro load')['Without offloading']

	key_list, traffic_demand_df_group = grouping_by_macro_load(traffic_demand_df)
	key_list, origin_macro_load_group = grouping_by_macro_load(origin_macro_load_df)
	mean_traffic_demand = traffic_demand_df_group.mean().drop('base_macro_load', 1) / 1000  # GB
	mean_origin_macro_load = origin_macro_load_group.mean().drop('base_macro_load', 1)
	logger.info('\n{}'.format(mean_traffic_demand))
	logger.info('\n{}'.format(mean_origin_macro_load))


def plot_energy_efficiency(method_dict):
	energy_effi_df = get_column_data_frame(method_dict, 'energy efficiency')
	logger.info('\n{}'.format(energy_effi_df.describe()))
	# print(energy_effi_df.head(5))
	key_list, energy_effi_df_group = grouping_by_macro_load(energy_effi_df)
	mean_energy_effi = energy_effi_df_group.mean()
	mean_energy_effi = mean_energy_effi.drop('base_macro_load', 1)
	# # print(mean_energy_effi.columns)
	mean_energy_effi.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	mean_energy_effi.index.name = 'Macro load rate'
	ax = mean_energy_effi.plot(kind='bar', alpha=0.7, rot=0, width=0.8)
	plt.legend(loc='upper left', fontsize='large')
	plt.title('Energy efficiency comparison')
	plt.xlabel('Macro load rate', size=15)
	plt.ylabel('Energy efficiency (Mb/Joule)', size=15)


def plot_power_consumption(method_dict):
	power_consumption_df = get_column_data_frame(method_dict, 'power consumption')
	logger.info('\n{}'.format(power_consumption_df.mean() / 1000000))  # M joule
	key_list, power_df_group = grouping_by_macro_load(power_consumption_df)
	mean_power = power_df_group.mean() / 1000000
	mean_power = mean_power.drop('base_macro_load', 1)
	mean_power.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	mean_power.index.name = 'Macro load rate'
	mean_power.plot(kind='bar', alpha=0.7, rot=0, width=0.8, figsize=(8, 6))
	plt.legend(loc='upper left', fontsize='large')
	plt.title('Energy consumption comparison')
	plt.xlabel('Macro load rate', size=15)
	plt.ylabel('Average energy consumption (MJoule)', size=15)  # per cell


def plot_energy_saving(method_dict):
	fig = plt.figure()
	ax_1 = fig.add_subplot(1, 1, 1)
	# ax_2 = fig.add_subplot(2, 1, 2)
	power_consumption_df = get_column_data_frame(method_dict, 'power consumption')
	key_list, power_df_group = grouping_by_macro_load(power_consumption_df)
	mean_power = power_df_group.mean() / 1000000  # M joule
	mean_power = mean_power.drop('base_macro_load', 1)
	mean_power.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	mean_power.index.name = 'Macro load rate'
	power_saving_rate = mean_power.apply(lambda x: (x['Without offloading'] - x[['Offloading without prefiction', 'Offloading with prediction']]) * 100 / x['Without offloading'], axis=1)
	# power_saving_rate = sum_power.apply(lambda x: (x['Offloading without prefiction'] - x['Offloading with prediction']) * 100 / x['Offloading without prefiction'], axis=1)
	# print(power_saving_rate)
	# power_save_rate_perdiction = (sum_power.loc[:, 'Without offloading'] - sum_power.loc[:, 'Offloading without prefiction']) / sum_power.loc[:, 'Without offloading']
	# power_save_rate_wihtou_perdiction = (sum_power.loc[:, 'Without offloading'] - sum_power.loc[:, 'Offloading without prefiction']) / sum_power.loc[:, 'Without offloading']
	power_saving_rate.plot(ax=ax_1, kind='bar', alpha=0.7, rot=0, width=0.8, color=['C2', 'C3'])
	ax_1.legend(loc='upper left', fontsize='large')
	ax_1.set_title('Power saving rate comparison')
	ax_1.set_xlabel('Macro load rate', size=15)
	ax_1.set_ylabel('Power saving rate (%)', size=15)

	# power_saving = sum_power.apply(lambda x: x['Without offloading'] - x[['Offloading without prefiction', 'Offloading with prediction']], axis=1)
	# print(power_saving)
	# power_saving.plot(ax=ax_2, kind='bar', alpha=0.7, rot=0)
	# ax_2.legend(loc='upper left', fontsize='large')
	# ax_2.set_title('Power saving comparison')
	# ax_2.set_xlabel('Macro load rate', size=15)
	# ax_2.set_ylabel('Power saving (MW)', size=15)


def plot_cell_load(method_dict):
	fig = plt.figure('cell loading rate', figsize=(10, 6))
	ax_1 = fig.add_subplot(3, 1, 1)
	ax_2 = fig.add_subplot(3, 1, 2)
	ax_3 = fig.add_subplot(3, 1, 3)

	macro_load_df = get_column_data_frame(method_dict, 'macro load')
	key_list, macro_load_df_group = grouping_by_macro_load(macro_load_df)
	macro_load = macro_load_df_group.mean()
	macro_load = macro_load.drop('base_macro_load', 1)
	macro_load.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	macro_load.index.name = 'Macro load rate'
	macro_load.plot(ax=ax_1, kind='bar', alpha=0.7, rot=0, width=0.8)
	ax_1.legend(loc='upper left', fontsize='x-large')
	ax_1.set_title('Cell loading comparison', size=18)
	ax_1.set_xlabel('', size=0)
	ax_1.set_ylim(0., 3)

	ax_1.set_ylabel('Macro cell load rate \n after offloading', size=14)

	small_load_df = get_column_data_frame(method_dict, 'small load')
	key_list, small_load_df_group = grouping_by_macro_load(small_load_df)
	small_load = small_load_df_group.mean()
	small_load = small_load.drop('base_macro_load', 1)
	small_load.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']

	small_load.index.name = 'Macro loading rate'
	# small_load = small_load[['Offloading without prefiction', 'Offloading with prediction']]
	small_load.plot(ax=ax_2, kind='bar', alpha=0.7, rot=0, width=0.8)
	ax_2.legend(loc='upper left', fontsize='large')
	ax_2.set_ylim(0., 1)
	# ax_2.set_title('Small cell load comparison')
	# ax_2.set_xlabel('Macro cell load rate', size=12)
	ax_2.set_xlabel('')
	ax_2.set_ylabel('Small cell loading rate', size=14)


	small_cell_num_df = get_column_data_frame(method_dict, 'small cell number')
	key_list, small_num_df_group = grouping_by_macro_load(small_cell_num_df)
	small_num = small_num_df_group.mean()
	small_num = small_num.drop('base_macro_load', 1)
	small_num.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']

	small_num.index.name = 'Macro load rate'
	# small_load = small_load[['Offloading without prefiction', 'Offloading with prediction']]
	small_num.plot(ax=ax_3, kind='bar', alpha=0.7, rot=0, width=0.8)
	ax_3.legend(loc='upper left', fontsize='large')
	# ax_2.set_title('Small cell load comparison')
	ax_3.set_xlabel('Macro cell loading rate', size=16)
	ax_3.set_ylabel('Small cell average number', size=14)

	ax_2.legend_.remove()
	ax_3.legend_.remove()

	for p in ax_1.patches:
		string = '{:.2f}'.format(float(p.get_height()))
		ax_1.annotate(string, xy=(p.get_x(), p.get_height()))
	for p in ax_2.patches:
		string = '{:.2f}'.format(float(p.get_height()))
		ax_2.annotate(string, xy=(p.get_x(), p.get_height()))
	for p in ax_3.patches:
		string = '{:.2f}'.format(float(p.get_height()))
		ax_3.annotate(string, xy=(p.get_x(), p.get_height()))


def plot_traffic_digested(method_dict):
	traffic_digested_df = get_column_data_frame(method_dict, 'traffic digested')
	logger.info('\n{}'.format(traffic_digested_df.mean() / 1000))  # Gb
	# print(energy_effi_df.head(5))
	key_list, traffic_df_group = grouping_by_macro_load(traffic_digested_df)
	mean_traffic = traffic_df_group.mean() / 1000  # Gb
	mean_traffic = mean_traffic.drop('base_macro_load', 1)
	# # print(mean_energy_effi.columns)
	mean_traffic.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	mean_traffic.index.name = 'Macro load rate'
	ax = mean_traffic.plot(kind='bar', alpha=0.7, rot=0, width=0.8)
	plt.legend(loc='upper left', fontsize='large')
	plt.title('Internet traffic digestion comparison')
	plt.xlabel('Macro loading rate', size=15)
	plt.ylabel('Internet traffic (Gb)', size=15)


def plot_energy_efficiency_energy_consump_traffic_throughput(method_dict):
	traffic_digested_df = get_column_data_frame(method_dict, 'traffic digested')
	energy_consumption_df = get_column_data_frame(method_dict, 'power consumption')
	energy_effi_df = get_column_data_frame(method_dict, 'energy efficiency')

	key_list, traffic_throughput_df_group = grouping_by_macro_load(traffic_digested_df)
	key_list, energy_consumption_df_group = grouping_by_macro_load(energy_consumption_df)
	key_list, energy_effi_df_group = grouping_by_macro_load(energy_effi_df)

	mean_traffic_throughput = traffic_throughput_df_group.mean().drop('base_macro_load', 1) / 1000  # Gb
	mean_energy_consumption = energy_consumption_df_group.mean().drop('base_macro_load', 1) / 1000000  # M joule
	mean_energy_effi = energy_effi_df_group.mean().drop('base_macro_load', 1)

	mean_traffic_throughput.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	mean_traffic_throughput.index.name = 'Macro loading rate'
	mean_energy_consumption.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	mean_energy_consumption.index.name = 'Macro loading rate'
	mean_energy_effi.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
	mean_energy_effi.index.name = 'Macro loading rate'

	fig = plt.figure('Energy power EE', figsize=(10, 6))
	ax_1 = fig.add_subplot(3, 1, 1)
	ax_2 = fig.add_subplot(3, 1, 2)
	ax_3 = fig.add_subplot(3, 1, 3)
	mean_energy_effi.plot(ax=ax_1, kind='bar', alpha=0.7, rot=0, width=0.8)
	mean_energy_consumption.plot(ax=ax_2, kind='bar', alpha=0.7, rot=0, width=0.8)
	mean_traffic_throughput.plot(ax=ax_3, kind='bar', alpha=0.7, rot=0, width=0.8)

	ax_1.legend(loc='upper left', fontsize='x-large')
	ax_1.set_title('Energy efficiency comparison', size=18)
	ax_1.set_xlabel('', size=0)
	ax_1.set_ylabel('Energy efficiency\n(Mb/Joule)', size=14)

	ax_2.legend(loc='upper left', fontsize='large')
	ax_2.set_xlabel('')
	ax_2.set_ylabel('Energy comsumption\n(M-Joule)', size=14)

	ax_3.legend(loc='upper left', fontsize='large')
	ax_3.set_xlabel('Macro cell loading rate group', size=17)
	ax_3.set_ylabel('Mobile traffic throughput\n(Gb)', size=14)

	ax_2.legend_.remove()
	ax_3.legend_.remove()

	for p in ax_1.patches:
		string = '{:.3f}'.format(float(p.get_height()))
		ax_1.annotate(string, xy=(p.get_x(), p.get_height()))
	for p in ax_2.patches:
		string = '{:.0f}'.format(float(p.get_height()))
		ax_2.annotate(string, xy=(p.get_x(), p.get_height()))
	for p in ax_3.patches:
		string = '{:.0f}'.format(float(p.get_height()))
		ax_3.annotate(string, xy=(p.get_x(), p.get_height()))


def ananlyzie_each_method():
	prediction_offloading_RL_path = os.path.join(root_dir, 'offloading/result/with_preidction_with_RL', 'all_cell_result_array_0731.npy')
	without_offloading_RL_path = os.path.join(root_dir, 'offloading/result/without_offloading_without_RL', 'all_cell_result_array_0731.npy')
	offloading_without_RL_path = os.path.join(root_dir, 'offloading/result/offloading_without_RL', 'all_cell_result_array_0731.npy')
	# God_prediction_offload_RL_path = os.path.join(root_dir, 'offloading/result/RL_with_god_prediction', 'all_cell_result_array.npy')
	# offloading_RL_without_prediction_path = os.path.join(root_dir, 'offloading/result/RL_without_prediction', 'all_cell_result_array_0726.npy')
	_10mins_offloading_RL_without_prediction_path = os.path.join(root_dir, 'offloading/result/RL_10mins_without_prediction', 'all_cell_result_array_0731.npy')
	offloading_q_table_path = os.path.join(root_dir, 'offloading/result/with_Q_table_without_prediction', 'all_cell_result_array_0928.npy')

	prediction_offloading_RL = get_dataframe(prediction_offloading_RL_path)
	without_offloading_RL = get_dataframe(without_offloading_RL_path)
	offloading_without_RL = get_dataframe(offloading_without_RL_path)
	_10mins_offloading_RL_without_prediction = get_dataframe(_10mins_offloading_RL_without_prediction_path)
	offloading_with_Q_table = get_dataframe(offloading_q_table_path)

	method_dict = OrderedDict()
	method_dict['Without offloading'] = without_offloading_RL
	method_dict['Offloading without RL'] = offloading_without_RL
	method_dict['Offloading with Q table'] = offloading_with_Q_table
	method_dict['Offloading without prediction (DQN)'] = _10mins_offloading_RL_without_prediction
	method_dict['Offloading with prediction (DQN)'] = prediction_offloading_RL


	# analysis_origin_macro_load_group(method_dict)
	plot_energy_efficiency(method_dict)
	# plot_power_consumption(method_dict)
	# plot_traffic_digested(method_dict)
	# plot_energy_saving(method_dict)

	''' the two main plot function'''
	# plot_cell_load(method_dict)
	# plot_energy_efficiency_energy_consump_traffic_throughput(method_dict)
	# analysis_low_load(method_dict)
	plt.show()


def comparison_predicion_and_without_prediction():
	def get_array(file_path):
		data_array = du.load_array(file_path)
		data_array = data_array[:, -149:, (0, 4)]
		return data_array
	prediction_offloading_RL_path = os.path.join(root_dir, 'offloading/result/with_preidction_with_RL', 'all_cell_result_array_0731.npy')
	_10mins_offloading_RL_without_prediction_path = os.path.join(root_dir, 'offloading/result/RL_10mins_without_prediction', 'all_cell_result_array_0731.npy')
	without_offloading_RL_path = os.path.join(root_dir, 'offloading/result/without_offloading_without_RL', 'all_cell_result_array_0731.npy')
	ARIMA_prediction_offloading_RL_path = os.path.join(root_dir, 'offloading/result/RL_real_ARIMA_prediction', 'all_cell_result_array_0805.npy')
	offloading_with_Q_table_path = os.path.join(root_dir, 'offloading/result/with_Q_table_without_prediction', 'all_cell_result_array_0927.npy')

	prediction_offloading_RL = get_array(prediction_offloading_RL_path)
	_10mins_offloading_RL_without_prediction = get_array(_10mins_offloading_RL_without_prediction_path)
	without_offloading_RL = get_array(without_offloading_RL_path)
	ARIMA_prediction_offloading_RL = get_array(ARIMA_prediction_offloading_RL_path)
	offloading_with_Q_table = get_array(offloading_with_Q_table_path)

	def overload_comparison():
		def count_overload(cell_list, load_array):
			overload_count = 0
			for cell in cell_list:
				for cell_index in range(load_array.shape[0]):
					if cell == load_array[cell_index, 0, 0]:
						cell_load_array = load_array[cell_index, :, 1]
						count = (cell_load_array > 1).sum()
						# print(cell, count)
						# count = (cell_load_array > 200).sum()
						overload_count += count

			return overload_count
		load_groups_dict = get_groups_load_dict()
		for key, group_list in load_groups_dict.items():
			without_prediction_overload_count = count_overload(group_list, _10mins_offloading_RL_without_prediction)
			prediction_overload_count = count_overload(group_list, prediction_offloading_RL)
			print('{} overload times: without prediction:{} with prediction:{}'.format(key, without_prediction_overload_count, prediction_overload_count))
		# without_offloading_RL_count = count_overload(group_list, without_offloading_RL)
		# print(without_offloading_RL_count)

	def macro_load_distribution():
		def group_array(load_groups_dict, load_array):
			'''
			find cell number from load array in with load group by load_groups_dict
			'''
			for key, load_cell_list in load_groups_dict.items():  # loop load_groups_dict
				cell_list = []
				for load_cell_index in range(load_array.shape[0]):  # loop load array cell
					cell_num = load_array[load_cell_index, 0, 0]
					if cell_num in load_cell_list:
						cell_list.append(load_array[load_cell_index, :, 1])

				group_cell_load_array = np.stack(cell_list)
				yield group_cell_load_array

		def plot_count_bar(data_frame):
			'''plot each group's new loading rate after offloading'''

			# bins = np.arange(0, 1.1, 0.1, dtype=np.float)
			# print(data_frame)
			bins = (0, 0.3, 0.7, 1, 2, 10)
			cats_Prediction_pd = pd.cut(data_frame['Prediction'], bins)
			cats_non_Prediction_pd = pd.cut(data_frame['Non prediction'], bins)
			cats_ARIMA_prediction_pd = pd.cut(data_frame['ARIMA prediction'], bins)
			cats_Q_table_pd = pd.cut(data_frame['Q table'], bins)

			Prediction_group = data_frame['Prediction'].groupby(cats_Prediction_pd)
			non_prediction_group = data_frame['Non prediction'].groupby(cats_non_Prediction_pd)
			ARIMA_prediction_group = data_frame['ARIMA prediction'].groupby(cats_ARIMA_prediction_pd)
			Q_table_group = data_frame['Q table'].groupby(cats_Q_table_pd)

			# print(non_prediction_group.mean())
			Prediction_group_counts = Prediction_group.count()
			non_prediction_counts = non_prediction_group.count()
			ARIMA_prediction_counts = ARIMA_prediction_group.count()
			Q_table_counts = Q_table_group.count()
			# print(Prediction_group_counts)
			count_df = pd.concat([Q_table_counts, non_prediction_counts, Prediction_group_counts, ARIMA_prediction_counts], axis=1)
			count_df.columns = ['Offloading with Q table', 'Offloading without prediction (DQN)', 'Offloading with CNN-RNN prediction (DQN)', 'Offloading with ARIMA prediction (DQN)']
			count_df.index = ['0~0.3', '0.3~0.7', '0.7~1', '1~2', '2~10']
			fig = plt.figure(figsize=(15, 6))
			ax = fig.add_subplot(1, 1, 1)
			ax = count_df.plot(ax=ax, kind='bar', color=['C2', 'C3', 'C4', 'C5'], alpha=0.7, rot=0, width=0.8)
			ax.set_title('Macro cell loading rate distributinon after offloading', size=18)
			ax.set_xlabel('Macro cell loading rate group', size=14)
			ax.set_ylabel('Times', size=14)
			ax.legend(loc='upper right', fontsize='large')
			for p in ax.patches:
				string = '{}'.format(int(p.get_height()))
				ax.annotate(string, xy=(p.get_x(), p.get_height()))

		load_groups_dict = get_groups_load_dict()

		""" non prediction case """
		offloading_with_Q_table_generator = group_array(load_groups_dict, offloading_with_Q_table)
		non_prediction_group_load_array_generator = group_array(load_groups_dict, _10mins_offloading_RL_without_prediction)

		"""prediction case"""
		ARIMA_prediction_group_load_array_generator = group_array(load_groups_dict, ARIMA_prediction_offloading_RL)
		prediction_group_load_array_generator = group_array(load_groups_dict, prediction_offloading_RL)

		'''from low loading to higher loading'''
		for group_prediction_load_array in prediction_group_load_array_generator:
			non_prediction_group_load_array = next(non_prediction_group_load_array_generator)
			ARIMA_prediction_group_load_array = next(ARIMA_prediction_group_load_array_generator)
			Q_table_group_load_array = next(offloading_with_Q_table_generator)

			group_prediction_load_array = group_prediction_load_array.reshape((-1, ))
			non_prediction_group_load_array = non_prediction_group_load_array.reshape((-1, ))
			ARIMA_prediction_group_load_array = ARIMA_prediction_group_load_array.reshape((-1, ))
			Q_table_group_load_array = Q_table_group_load_array.reshape((-1, ))

			macro_load_df = pd.DataFrame({
				'Prediction': group_prediction_load_array,
				'Non prediction': non_prediction_group_load_array,
				'ARIMA prediction': ARIMA_prediction_group_load_array,
				'Q table': Q_table_group_load_array})
			# macro_load_df.plot(kind='line')
			# print(macro_load_df.describe())
			'''plot each group's new loading rate after offloading'''
			plot_count_bar(macro_load_df)

		plt.show()

	overload_comparison()
	macro_load_distribution()


if __name__ == "__main__":
	analysis_energy_effi()
	# ananlyzie_each_method()
	# comparison_predicion_and_without_prediction()
