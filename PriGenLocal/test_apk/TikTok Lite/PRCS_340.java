/*Application Package Name: com.tiktok.lite.go
class PRCS_340 {
/**
X.5W6;lambda$cYEA371qaZS1oio0IA0fPZ1iBa4(LX/5W6;)V
*/

    public static synthetic void lambda$cYEA371qaZS1oio0IA0fPZ1iBa4(X.5W6 p21)
    {
        try {
            String v1_0 = X.16B.LB;
            p21.LB = -1;
            android.net.ConnectivityManager v10_1 = ((android.net.ConnectivityManager) v1_0.getSystemService("connectivity"));
            p21.LBL = ((android.telephony.TelephonyManager) v1_0.getSystemService("phone"));
            p21.L(android.telephony.SubscriptionManager.getDefaultDataSubscriptionId());
            String v1_2 = new android.net.NetworkRequest$Builder();
            v1_2.addCapability(12).addTransportType(0);
            X.5W4 v3_1 = new X.5W4(p21);
            android.net.NetworkRequest v2_1 = v1_2.build();
            com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v11 = new Object[2];
            v11[0] = v2_1;
            v11[1] = v3_1;
            com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/NetworkRequest;Landroid/net/ConnectivityManager$NetworkCallback;)V", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOapbZzLyHyJ5ssDB2nYTlkzwJ5jEqd8VMq/WjvM");
        } catch (Exception) {
            return;
        }
        if (!v5_1.preInvoke(85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, "void", v12_1).intercept) {
            v10_1.registerNetworkCallback(v2_1, v3_1);
            v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, v12_1, 1);
        } else {
            v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, v12_1, 0);
        }
        X.5W7.LB = 1;
        return;
    }

/**
com.ss.android.ugc.aweme.lancet.-;run()V
*/

    public final void run()
    {
        X.5W6.lambda$cYEA371qaZS1oio0IA0fPZ1iBa4(this.f$0);
        return;
    }


}