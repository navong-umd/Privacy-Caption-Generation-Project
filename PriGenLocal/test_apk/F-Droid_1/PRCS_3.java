/* Application Package Name: org.fdroid.fdroid */
class PRCS_3 {
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


}
