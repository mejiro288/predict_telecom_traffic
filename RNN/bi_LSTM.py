import numpy as np
import tensorflow as tf
import tensorlayer as tl
from sklearn import preprocessing
import matplotlib.pyplot as plt
import sys
import os
sys.path.append('/home/mldp/ML_with_bigdata')
import data_utility as du

root_dir = '/home/mldp/ML_with_bigdata'


def get_data():
	grid_start = 55
	grid_stop = 56
	filelist = du.list_all_input_file(root_dir + '/npy/hour_max/X')
	filelist.sort()

	X_list = []
	Y_list = []
	for i, filename in enumerate(filelist):
		data_array = du.load_array(root_dir + '/npy/hour_max/X/' + filename)
		data_array = data_array[:, :, grid_start:grid_stop, grid_start:grid_stop, -1, np.newaxis]
		X_list.append(data_array)

	filelist = du.list_all_input_file(root_dir + '/npy/hour_max/Y')
	filelist.sort()
	for i, filename in enumerate(filelist):
		data_array = du.load_array(root_dir + '/npy/hour_max/Y/' + filename)
		data_array = data_array[:, :, grid_start:grid_stop, grid_start:grid_stop, -1, np.newaxis]
		Y_list.append(data_array)

	X_array = np.concatenate(X_list, axis=0)
	Y_array = np.concatenate(Y_list, axis=0)
	X_array = X_array[:-1]  # important
	Y_array = Y_array[1:]  # important
	print('X data array shape', X_array.shape)
	print('Y data array shape', Y_array.shape)
	return X_array, Y_array


def feature_scaling(input_data, scaler=None):
	input_shape = input_data.shape
	input_data = input_data.reshape(-1, 1)
	if scaler:
		output = scaler.transform(input_data)
	else:
		scaler = preprocessing.MinMaxScaler(feature_range=(0.1, 255))
		output = scaler.fit_transform(input_data)
	return output.reshape(input_shape), scaler


def unfeautre_scaling(input_data, scaler):
	input_shape = input_data.shape
	input_data = input_data.reshape(-1, 1)
	output = scaler.inverse_transform(input_data)
	output = output.reshape(input_shape)
	return output


class biRNN:
	def __init__(self):
		self.Xs = tf.placeholder(tf.float32, shape=[None, 6, 1, 1, 1])
		self.Ys = tf.placeholder(tf.float32, shape=[None, 1, 1, 1, 1])
		self.batch_size = 100
		tl_rnn_output = self._build_BI_RNN(self.Xs)
		network = tl.layers.FlattenLayer(tl_rnn_output, name='flatten_layer')
		network = tl.layers.BatchNormLayer(network, name='batchnorm_layer_1')
		network = tl.layers.DenseLayer(network, W_init=tf.contrib.layers.xavier_initializer_conv2d(), n_units=128, act=lambda x: tl.act.lrelu(x, 0.2), name='fully_connect_1')
		network = tl.layers.DropoutLayer(network, keep=0.8, name='drop_1')
		network = tl.layers.DenseLayer(network, W_init=tf.contrib.layers.xavier_initializer_conv2d(), n_units=1, act=tl.activation.identity, name='fully_connect_2')

		self.tl_output = tl.layers.ReshapeLayer(network, shape=[-1, 1, 1, 1, 1], name='reshape_layer')
		self.regression_output = self.tl_output.outputs

		self.MSE = tf.reduce_mean(tf.pow(self.regression_output - self.Ys, 2), name='MSE_op')
		# MAPE = tf.reduce_mean(tf.divide(tf.abs(self.Ys - self.regression_output), tf.reduce_mean(self.Ys)), name='MAPE_OP')
		MAPE = tf.reduce_mean(tf.divide(tf.abs(self.Ys - self.regression_output), self.Ys), name='MAPE_OP')

		self.accuracy = 1 - MAPE
		optimizer = tf.train.AdamOptimizer(learning_rate=0.0001)

		opt_vars = tf.trainable_variables()
		gvs = optimizer.compute_gradients(self.MSE, var_list=opt_vars)
		capped_gvs = [(tf.clip_by_norm(grad, 5), var) for grad, var in gvs if grad is not None]
		self.optimizer_op = optimizer.apply_gradients(capped_gvs)
		self.saver = tf.train.Saver()
	
	def _build_BI_RNN(self, input_X):
		with tf.variable_scope('RNN'):
			network = tl.layers.InputLayer(input_X, name='input_layer')
			network = tl.layers.ReshapeLayer(network, shape=[-1, 6, 1], name='reshape_layer_1')
			network = tl.layers.BatchNormLayer(network, name='batchnorm_layer_1')
			network = tl.layers.BiRNNLayer(
				network,
				cell_fn=tf.nn.rnn_cell.LSTMCell,
				n_hidden=128,
				initializer=tf.random_uniform_initializer(-0.1, 0.1),
				n_steps=6,
				fw_initial_state=None,
				bw_initial_state=None,
				return_last=True,
				return_seq_2d=False,
				n_layer=3,
				dropout=(0.9, 0.9),
				name='layer_1')
		return network

	def _build_RNN(self, input_X):
		with tf.variable_scope('RNN'):
			network = tl.layers.InputLayer(input_X, name='input_layer')
			network = tl.layers.ReshapeLayer(network, shape=[-1, 6, 1], name='reshape_layer_1')
			network = tl.layers.BatchNormLayer(network, name='batchnorm_layer_1')
			network = tl.layers.RNNLayer(
				network,
				cell_fn=tf.nn.rnn_cell.LSTMCell,
				# cell_init_args={'forget_bias': 0.0},
				n_hidden=128,
				initializer=tf.random_uniform_initializer(-0.1, 0.1),
				n_steps=6,
				initial_state=None,
				return_last=False,
				return_seq_2d=False,  # trigger with return_last is False. if True, return shape: (?, 200); if False, return shape: (?, 6, 200)
				name='layer_1')
			network = tl.layers.DropoutLayer(network, keep=0.85, name='drop_1')
			network = tl.layers.RNNLayer(
				network,
				cell_fn=tf.nn.rnn_cell.LSTMCell,
				# cell_init_args={'forget_bias': 0.0},
				n_hidden=128,
				initializer=tf.random_uniform_initializer(-0.1, 0.1),
				n_steps=6,
				initial_state=None,
				return_last=False,
				return_seq_2d=False,  # trigger with return_last is False. if True, return shape: (?, 200); if False, return shape: (?, 6, 200)
				name='layer_2')
			network = tl.layers.DropoutLayer(network, keep=0.85, name='drop_2')
			network = tl.layers.RNNLayer(
				network,
				cell_fn=tf.nn.rnn_cell.LSTMCell,
				# cell_init_args={'forget_bias': 0.0},
				n_hidden=128,
				initializer=tf.random_uniform_initializer(-0.1, 0.1),
				n_steps=6,
				initial_state=None,
				return_last=True,
				return_seq_2d=False,  # trigger with return_last is False. if True, return shape: (?, 200); if False, return shape: (?, 6, 200)
				name='layer_3')
			network = tl.layers.DropoutLayer(network, keep=0.85, name='drop_3')
		return network

	def _batch_data(self, X_, Y_, shuffle=None):
		batch_len = len(X_) // self.batch_size
		z = list(zip(X_, Y_))
		if shuffle:
			np.random.shuffle(z)
		for batch_index in range(batch_len + 1):
			batch_x, batch_y = zip(*z[batch_index * self.batch_size: (batch_index + 1) * self.batch_size])
			yield np.array(batch_x), np.array(batch_y)

	def _test(self, sess, X_, Y_):
		batch_iter = self._batch_data(X_, Y_)
		accu_cue = 0
		mse_cue = 0
		predict_list = []
		for index, batch in enumerate(batch_iter):
			batch_x, batch_y = batch
			dp_dict = tl.utils.dict_to_one(self.tl_output.all_drop)
			feed_dict = {
				self.Xs: batch_x,
				self.Ys: batch_y}
			feed_dict.update(dp_dict)
			MSE, accu, predict = sess.run([self.MSE, self.accuracy, self.regression_output], feed_dict=feed_dict)
			accu_cue += accu
			mse_cue += MSE
			# print(predict.shape)
			predict_list.append(predict)
		predict = np.concatenate(predict_list, axis=0)
		return mse_cue / (index + 1), accu_cue / (index + 1), predict

	def fit(self, X_, Y_):
		plt.ion()
		fig_1 = plt.figure(0)
		fig_2 = plt.figure(1)
		fig_3 = plt.figure(2)

		training_accu_hist = []
		training_loss_hist = []

		valiation_accu_hist = []
		valiation_loss_hist = []

		data_len = X_.shape[0]
		X_train, X_valid = X_[: 9 * data_len // 10], X_[9 * data_len // 10:]
		Y_train, Y_valid = Y_[: 9 * data_len // 10], Y_[9 * data_len // 10:]
		print('x train shape:{} X valid shape:{}'.format(X_train.shape, X_valid.shape))
		print('y train shape:{} y valid shape:{}'.format(Y_train.shape, Y_valid.shape))

		def plot_loss_accu(fig_instance, training_accu_hist, training_loss_hist, valid_accu_hist, valid_loss_hist):
			ax_1 = fig_instance.add_subplot(2, 1, 1)
			ax_2 = fig_instance.add_subplot(2, 1, 2)
			ax_1.cla()
			ax_2.cla()

			ax_1.plot(training_accu_hist, 'g-', label='training accu')
			ax_1.plot(valid_accu_hist, 'r-', label='valiation accu')
			ax_1.legend()
			ax_1.grid()

			ax_2.plot(training_loss_hist, 'g-', label='training loss')
			ax_2.plot(valid_loss_hist, 'r-', label='valiation loss')
			ax_2.legend()
			ax_2.grid()

		def plot_predict_vs_real(fig_instance, real, predict, title=None):
			ax_1 = fig_instance.add_subplot(2, 1, 1)
			ax_2 = fig_instance.add_subplot(2, 1, 2)

			ax_1.cla()
			ax_2.cla()

			ax_1.plot(real[0:72, 0, 0, 0, 0], 'b-', label='real', marker='.')
			ax_1.plot(predict[0:72, 0, 0, 0, 0], 'r-', label='predict', marker='.')
			ax_1.grid()
			ax_1.legend()
			ax_1.set_title(title)

			ax_2.plot(real[72:144, 0, 0, 0, 0], 'b-', label='real', marker='.')
			ax_2.plot(predict[72:144, 0, 0, 0, 0], 'r-', label='predict', marker='.')
			ax_2.grid()
			ax_2.legend()

		with tf.Session() as sess:
			sess.run(tf.global_variables_initializer())
			for epoch in range(1000):
				batch_iter = self._batch_data(X_train, Y_train, shuffle=True)
				for batch_x, batch_y in batch_iter:
					feed_dict = {
						self.Xs: batch_x,
						self.Ys: batch_y}
					feed_dict.update(self.tl_output.all_drop)
					_ = sess.run([self.optimizer_op], feed_dict=feed_dict)

				if epoch % 10 == 0 and epoch is not 0:
					mse, accu, predict = self._test(sess, X_train, Y_train)
					print('Training: epoch:{} mse:{} accu:{}'.format(epoch, mse, accu))
					training_accu_hist.append(accu)
					training_loss_hist.append(mse)

					plot_predict_vs_real(fig_1, Y_train, predict, 'training data')
					'''valiation'''
					mse, accu, predict = self._test(sess, X_valid, Y_valid)
					print('Valiation epoch:{} mse:{} accu:{}'.format(epoch, mse, accu), end='\n\n')
					valiation_accu_hist.append(accu)
					valiation_loss_hist.append(mse)
					plot_predict_vs_real(fig_2, Y_valid, predict, 'valiation data')

					'''loss accu'''
					plot_loss_accu(fig_3, training_accu_hist, training_loss_hist, valiation_accu_hist, valiation_loss_hist)

					plt.pause(0.001)
			print('training finish')
			self.saver.save(sess, './output_model/temp.ckpt')
		plt.ioff()
		plt.show()

	def predict(self, X_test, Y_test):
		with tf.Session() as sess:
			self.saver.restore(sess, './output_model/temp.ckpt')
			mse, accu, predict = self._test(sess, X_test, Y_test)
			print('mse:{} accu:{}'.format(mse, accu))
		return predict


def evaluation(real, predict):
	print(real.shape, predict.shape)

	def MAPE(real, predict):
		AE = np.absolute(real - predict)
		MAPE = np.divide(AE, real)
		MAPE_mean = MAPE.mean()
		print('accuracy:{:.4f}'.format(1 - MAPE_mean))

	MAPE(real, predict)

	plt.figure()
	plt.plot(real[:, 0, 0, 0, 0], 'b-', label='real', marker='.')
	plt.plot(predict[:, 0, 0, 0, 0], 'r-', label='predict', marker='.')
	plt.legend()
	plt.grid()
	plt.show()

if __name__ == '__main__':
	X_data, Y_data = get_data()
	X_data, scaler = feature_scaling(X_data)
	Y_data, scaler = feature_scaling(Y_data, scaler)
	data_len = X_data.shape[0]
	X_train, X_test = X_data[: 9 * data_len // 10], X_data[9 * data_len // 10:]
	print('x train shape:{} X test shape:{}'.format(X_train.shape, X_test.shape))
	Y_train, Y_test = Y_data[: 9 * data_len // 10], Y_data[9 * data_len // 10:]
	print('y train shape:{} y test shape:{}'.format(Y_train.shape, Y_test.shape))

	NN = biRNN()
	NN.fit(X_train[:, :, 0:1, 0:1], Y_train[:, :, 0:1, 0:1])

	predict = NN.predict(X_test[:, :, 0:1, 0:1], Y_test[:, :, 0:1, 0:1])
	# Y_test_unfeature = Y_test
	predict = unfeautre_scaling(predict, scaler)
	Y_test_unfeature = unfeautre_scaling(Y_test, scaler)
	evaluation(Y_test_unfeature[:, :, 0:1, 0:1], predict)
	'''
	predict = NN.predict(X_test[:, :, 2:3, 2:3], Y_test[:, :, 2:3, 2:3])
	predict = unfeautre_scaling(predict, scaler)
	Y_test_unfeature = unfeautre_scaling(Y_test, scaler)
	evaluation(Y_test_unfeature[:, :, 2:3, 2:3], predict)
	'''
