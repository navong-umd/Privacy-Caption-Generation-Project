/*Application Package Name: com.tiktok.lite.go
class PRCS_331 {
/**
com.ss.android.ugc.aweme.performance.ipc.IPCOptTask;run(Landroid/content/Context;)V
*/

    public final void run(android.content.Context p24)
    {
        if (X.5uK.LB().L) {
            X.5uU v1_0 = X.16B.LB;
            if ((X.5uK.LB().L) && ((v1_0 != null) && (!X.5uV.LB))) {
                X.5uV.LBL = new X.5uR(1, 0, 1);
                if (X.5uK.LB().LBL > 0) {
                    if (android.os.Build$VERSION.SDK_INT >= 24) {
                        int v3_2 = new android.net.NetworkRequest$Builder();
                        v3_2.addCapability(12);
                        android.net.ConnectivityManager v12_1 = ((android.net.ConnectivityManager) v1_0.getSystemService("connectivity"));
                        int v4_0 = v3_2.build();
                        int v3_3 = X.5uV.L;
                        android.net.ConnectivityManager v7_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v13 = new Object[2];
                        v13[0] = v4_0;
                        v13[1] = v3_3;
                        com.bytedance.helios.statichook.api.ExtraInfo v14_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/NetworkRequest;Landroid/net/ConnectivityManager$NetworkCallback;)V", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPqtcZnBzj9qpgzwML/bdcVI7LRnSbK7m10dcV+JNZw23VQk1w==");
                    }
                    try {
                        int v3_6 = new android.content.IntentFilter();
                        v3_6.addAction("android.net.conn.CONNECTIVITY_CHANGE");
                        v3_6.addAction("android.net.wifi.WIFI_STATE_CHANGED");
                        v3_6.addAction("android.net.wifi.STATE_CHANGE");
                        v3_6.setPriority(999);
                        X.5uV.L(v1_0.getApplicationContext(), new X.5uU(), v3_6);
                    } catch (Throwable) {
                    }
                    X.5uV.LB = 1;
                } else {
                    X.5uV.LB = 1;
                }
            }
        }
        X.75N.L(new Y.ARunnableS1S0000000_2(5));
        return;
    }


}