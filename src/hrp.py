import numpy as np
import scipy.cluster.hierarchy as sch
import scipy.spatial.distance as ssd


class HierarchicalRiskParity:
    """Copied from
        - https://pyportfolioopt.readthedocs.io/en/latest/_modules/pypfopt/hierarchical_portfolio.html#HRPOpt
        - https://github.com/hudson-and-thames/mlfinlab/blob/master/mlfinlab/portfolio_optimization/hrp.py
    The only modifications I made were to move all the datahandling from pandas to numpy arrays. 
    This resulted in a drastic speed up of nearly 20x (from 20ms to 1ms), thus making the 
    algorithm more suitable for repeated calls.
    """

    #     cdef:
    #         # init
    #         cnp.ndarray asset_names
    #         str linkage

    #         # get_cluster_var
    #         cnp.ndarray cov_slice
    #         cnp.float64_t[:] w

    #         # recursive_bisection
    #         dict weights
    #         list cluster_items, first_cluster, second_cluster
    #         cnp.ndarray first_variance, second_variance
    #         cnp.float64_t alpha
    #         int i, j, k, l

    #         # allocate
    #         cnp.ndarray asset_returns, correlation_matrix, covariance_matrix
    #         cnp.ndarray distance_matrix, clusters, ordered_indices, ordered_tickers
    def __init__(self, asset_names, linkage='single'):
        self.asset_names = np.array(asset_names)
        self.linkage = linkage

    @staticmethod
    def _get_cluster_var(covariance_matrix, cluster_items):
        """
        Compute the variance per cluster

        :param cov: covariance matrix
        :type cov: np.ndarray
        :param cluster_items: tickers in the cluster
        :type cluster_items: list
        :return: the variance per cluster
        :rtype: float
        """
        # Compute variance per cluster
        cov_slice = covariance_matrix[np.ix_(cluster_items, cluster_items)]
        w = 1 / np.diag(cov_slice)  # Inverse variance weights
        w /= w.sum()
        return np.linalg.multi_dot((w, cov_slice, w))

    def _allocate(self, cov, ordered_indices, ordered_tickers):
        """
        Given the clusters, compute the portfolio that minimises risk by
        recursively traversing the hierarchical tree from the top.
        """
        weights = np.ones_like(ordered_indices, dtype=np.float64)
        cluster_items = [ordered_indices]  # initialize all items in one cluster

        while len(cluster_items) > 0:
            cluster_items = [
                i[start:end]
                for i in cluster_items
                # halving algorithm
                # start -> first half
                # end -> second half
                for start, end in ((0, len(i) // 2), (len(i) // 2, len(i)))
                if len(i) > 1
            ]
            # bi-section
            # For each pair, optimise locally.
            for subcluster in range(0, len(cluster_items), 2):
                left_cluster = cluster_items[subcluster]
                right_cluster = cluster_items[subcluster + 1]

                # Form the inverse variance portfolio for this pair
                left_variance = self._get_cluster_var(cov, left_cluster)
                right_variance = self._get_cluster_var(cov, right_cluster)

                allocation_factor = 1 - left_variance / (right_variance + left_variance)
                weights[left_cluster] *= allocation_factor  # weight 1
                weights[right_cluster] *= 1 - allocation_factor  # weight 2

            return weights

    @staticmethod
    def build_long_short_portfolio(weights, side_weights):
        """
        Adjust weights according the shorting constraints specified.
        :param side_weights: (pd.Series/numpy matrix) With asset_names in index and value 1 for Buy, -1 for Sell
                                                      (default 1 for all)
        """

        short_ptf = np.where(side_weights == -1)
        buy_ptf = np.where(side_weights == 1)
        if len(short_ptf) > 0:

            # Short half size
            weights[short_ptf] /= np.sum(weights[short_ptf])
            weights[short_ptf] *= -0.5

            # Buy other half
            weights[buy_ptf] /= np.sum(weights[buy_ptf])
            weights[buy_ptf] *= 0.5

        return weights

    def optimize(self, asset_prices, side_weights):
        asset_returns = np.diff(asset_prices) / asset_prices[:, :-1]

        # Calculate covariance and correlation of returns
        covariance_matrix = np.cov(asset_returns, bias=False)
        correlation_matrix = np.corrcoef(asset_returns)

        # Calculate distance from covariance matrix
        distance_matrix = np.sqrt((1 - correlation_matrix).round(5) / 2)

        # Step-1: Tree Clustering
        clusters = sch.linkage(ssd.squareform(distance_matrix), method=self.linkage)

        # Step-2: Quasi Diagnalization
        ordered_indices = sch.to_tree(clusters, rd=False).pre_order()
        ordered_tickers = self.asset_names[ordered_indices]

        # Step-3: Recursive Bisection
        weights = self._allocate(covariance_matrix, ordered_indices, ordered_tickers)

        self.weights = weights

        weights = self.build_long_short_portfolio(weights, np.array(side_weights))
        
        return weights
