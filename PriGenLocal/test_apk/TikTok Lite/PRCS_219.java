/*Application Package Name: com.tiktok.lite.go
class PRCS_219 {
/**
com.google.android.gms.internal.gtm.be;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yz1cEJOnFpNPfG57TP3DlRLqg==");
            com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, "android.net.NetworkInfo", v10_1);
        } catch (android.net.NetworkInfo v0_3) {
            v0_3.printStackTrace();
            return X.1Mw.L();
        }
        if (!v1_0.intercept) {
            android.net.NetworkInfo v4_0 = p18.getActiveNetworkInfo();
            v3_1.postInvoke(v4_0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 1);
            return v4_0;
        } else {
            v3_1.postInvoke(0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 0);
            return ((android.net.NetworkInfo) v1_0.returnValue);
        }
    }

/**
com.google.android.gms.internal.gtm.be;LCC(Lcom/google/android/gms/internal/gtm/be;)Z
*/

    public static final boolean LCC(com.google.android.gms.internal.gtm.be p4)
    {
        android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) p4.LB.L.getSystemService("connectivity"));
        try {
            android.net.NetworkInfo v0_11;
            System.nanoTime();
        } catch (Exception) {
            return 0;
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = com.google.android.gms.internal.gtm.be.L(v3_1);
                        v0_11 = X.5uC.L;
                        if ((v0_11 == null) || (!v0_11.isConnected())) {
                            return 0;
                        } else {
                            return 1;
                        }
                    } else {
                        if (X.5uO.L) {
                            X.5uL.L("cm_net_info", com.google.android.gms.internal.gtm.be.L(v3_1).toString(), X.5uC.L.toString());
                        }
                        v0_11 = X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    v0_11 = com.google.android.gms.internal.gtm.be.L(v3_1);
                }
            } else {
                v0_11 = com.google.android.gms.internal.gtm.be.L(v3_1);
            }
        } else {
            v0_11 = com.google.android.gms.internal.gtm.be.L(v3_1);
        }
    }

/**
com.google.android.gms.internal.gtm.be;L(Landroid/content/Intent;)V
*/

    private void L(android.content.Intent p21)
    {
        com.google.android.gms.internal.gtm.be.LC(this);
        int v2_0 = p21.getAction();
        this.LB.L().L("NetworkBroadcastReceiver received action", v2_0);
        if (!"android.net.conn.CONNECTIVITY_CHANGE".equals(v2_0)) {
            if (!"com.google.analytics.RADIO_POWERED".equals(v2_0)) {
                this.LB.L().LC("NetworkBroadcastReceiver received unknown action", v2_0);
                return;
            } else {
                if (!p21.hasExtra(com.google.android.gms.internal.gtm.be.L)) {
                    String v1_2 = this.LB.LBL();
                    v1_2.LB("Radio powered up");
                    v1_2.LFI();
                    android.content.Context v9 = v1_2.LB.L;
                    if ((!X.3G7.L(v9)) || (!X.3G8.L(v9))) {
                        v1_2.L(0);
                        return;
                    } else {
                        android.content.Intent v3_2 = new android.content.Intent("com.google.android.gms.analytics.ANALYTICS_DISPATCH");
                        v3_2.setComponent(new android.content.ComponentName(v9, "com.google.android.gms.analytics.AnalyticsService"));
                        com.bytedance.helios.statichook.api.HeliosApiHook v4_2 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v10 = new Object[1];
                        v10[0] = v3_2;
                        com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/content/Intent;)Landroid/content/ComponentName;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yz1cEJOnFpNPfG57TP3DlRJpQ==");
                        if (!v4_2.preInvoke(11084, "android/content/Context", "startService", v9, v10, "android.content.ComponentName", v11_1).intercept) {
                            v4_2.postInvoke(v9.startService(v3_2), 11084, "android/content/Context", "startService", v9, v10, v11_1, 1);
                            return;
                        } else {
                            v4_2.postInvoke(0, 11084, "android/content/Context", "startService", v9, v10, v11_1, 0);
                        }
                    }
                }
                return;
            }
        } else {
            String v1_6 = com.google.android.gms.internal.gtm.be.LCC(this);
            if (this.LC != v1_6) {
                this.LC = v1_6;
                int v2_2 = this.LB.LBL();
                v2_2.L("Network connectivity status changed", Boolean.valueOf(v1_6));
                v2_2.LB.LB().L(new X.3GT(v2_2));
            }
            return;
        }
    }


}