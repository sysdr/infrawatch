/** Disable the full-screen "Compiled with problems" overlay so the dashboard stays visible. */
module.exports = {
  devServer: {
    client: {
      overlay: false,
    },
  },
};
