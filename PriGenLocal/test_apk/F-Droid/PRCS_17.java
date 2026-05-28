/*Application Package Name: org.fdroid.fdroid
class PRCS_17 {
/**
com.bumptech.glide.manager.SingletonConnectivityReceiver;isConnected()Z
*/

    boolean isConnected()
    {
        int v0 = 1;
        try {
            boolean v1_4 = ((android.net.ConnectivityManager) this.connectivityManager.get()).getActiveNetworkInfo();
        } catch (boolean v1_5) {
            if (android.util.Log.isLoggable("ConnectivityMonitor", 5)) {
                android.util.Log.w("ConnectivityMonitor", "Failed to determine connectivity status when connectivity changed", v1_5);
            }
            return 1;
        }
        if ((!v1_4) || (!v1_4.isConnected())) {
            v0 = 0;
        }
        return v0;
    }

/**
com.bumptech.glide.manager.SingletonConnectivityReceiver;run()V
*/

    public void run()
    {
        com.bumptech.glide.manager.SingletonConnectivityReceiver$FrameworkConnectivityMonitorPreApi24 v0_1 = this.this$0.isConnected;
        boolean v1_1 = this.this$0;
        v1_1.isConnected = v1_1.isConnected();
        if (v0_1 != this.this$0.isConnected) {
            if (android.util.Log.isLoggable("ConnectivityMonitor", 3)) {
                com.bumptech.glide.manager.SingletonConnectivityReceiver$FrameworkConnectivityMonitorPreApi24 v0_4 = new StringBuilder();
                v0_4.append("connectivity changed, isConnected: ");
                v0_4.append(this.this$0.isConnected);
                android.util.Log.d("ConnectivityMonitor", v0_4.toString());
            }
            com.bumptech.glide.manager.SingletonConnectivityReceiver$FrameworkConnectivityMonitorPreApi24 v0_6 = this.this$0;
            v0_6.notifyChangeOnUiThread(v0_6.isConnected);
        }
        return;
    }


}