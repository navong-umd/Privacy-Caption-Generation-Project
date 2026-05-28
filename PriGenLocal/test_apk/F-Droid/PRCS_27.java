/*Application Package Name: org.fdroid.fdroid
class PRCS_27 {
/**
androidx.work.impl.utils.NetworkApi24;m(Landroid/net/ConnectivityManager; Landroid/net/ConnectivityManager$NetworkCallback;)V
*/

    public static bridge synthetic void m(android.net.ConnectivityManager p0, android.net.ConnectivityManager$NetworkCallback p1)
    {
        p0.registerDefaultNetworkCallback(p1);
        return;
    }

/**
com.bumptech.glide.manager.SingletonConnectivityReceiver;register()Z
*/

    public boolean register()
    {
        RuntimeException v0_1;
        if (((android.net.ConnectivityManager) this.connectivityManager.get()).getActiveNetwork() == null) {
            v0_1 = 0;
        } else {
            v0_1 = 1;
        }
        this.isConnected = v0_1;
        try {
            androidx.work.impl.utils.NetworkApi24$$ExternalSyntheticApiModelOutline0.m(((android.net.ConnectivityManager) this.connectivityManager.get()), this.networkCallback);
            return 1;
        } catch (RuntimeException v0_5) {
            if (android.util.Log.isLoggable("ConnectivityMonitor", 5)) {
                android.util.Log.w("ConnectivityMonitor", "Failed to register callback", v0_5);
            }
            return 0;
        }
    }


}