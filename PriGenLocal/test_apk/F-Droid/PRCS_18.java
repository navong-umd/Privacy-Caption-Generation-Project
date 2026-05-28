/*Application Package Name: org.fdroid.fdroid
class PRCS_18 {
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
        com.bumptech.glide.manager.SingletonConnectivityReceiver$FrameworkConnectivityMonitorPreApi24 v0_0 = this.this$0;
        v0_0.isConnected = v0_0.isConnected();
        try {
            com.bumptech.glide.manager.SingletonConnectivityReceiver$FrameworkConnectivityMonitorPreApi24 v0_4 = this.this$0;
            v0_4.context.registerReceiver(v0_4.connectivityReceiver, new android.content.IntentFilter("android.net.conn.CONNECTIVITY_CHANGE"));
            this.this$0.isRegistered = 1;
        } catch (com.bumptech.glide.manager.SingletonConnectivityReceiver$FrameworkConnectivityMonitorPreApi24 v0_2) {
            if (android.util.Log.isLoggable("ConnectivityMonitor", 5)) {
                android.util.Log.w("ConnectivityMonitor", "Failed to register", v0_2);
            }
            this.this$0.isRegistered = 0;
        }
        return;
    }


}