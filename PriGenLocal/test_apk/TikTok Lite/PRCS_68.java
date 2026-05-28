/*Application Package Name: com.tiktok.lite.go
class PRCS_68 {
/**
X.5qE;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOStd9HA0zzZXPaD3yI+r/XszZH2Z8VmZaAeKnRB3DA0kU8HQidz");
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
X.5qE;LBL()Z
*/

    public static boolean LBL()
    {
        int v4 = 0;
        try {
            android.net.ConnectivityManager v3_1 = X.16B.LB.getSystemService("connectivity");
        } catch (Exception) {
            return v4;
        }
        if (v3_1 == null) {
            throw new NullPointerException("null cannot be cast to non-null type android.net.ConnectivityManager");
        } else {
            android.net.ConnectivityManager v3_0 = ((android.net.ConnectivityManager) v3_1);
            android.net.NetworkInfo v0_13;
            System.nanoTime();
            if (X.5uK.LB().L) {
                if ((X.75K.L()) || (X.5uK.LB().LB)) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.5qE.L(v3_0);
                            v0_13 = X.5uC.L;
                            if ((v0_13 != null) && (v0_13.isConnected())) {
                                v4 = 1;
                            }
                            return v4;
                        } else {
                            if (X.5uO.L) {
                                X.5uQ.L("cm_net_info", X.5qE.L(v3_0).toString(), X.5uC.L.toString());
                            }
                            v0_13 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v0_13 = X.5qE.L(v3_0);
                    }
                } else {
                    v0_13 = X.5qE.L(v3_0);
                }
            } else {
                v0_13 = X.5qE.L(v3_0);
            }
        }
    }

/**
Y.ARunnableS4S0100000_2;run$116(LY/ARunnableS4S0100000_2;)V
*/

    public static final void run$116(Y.ARunnableS4S0100000_2 p5)
    {
        if (X.5qE.LBL()) {
            if (!((X.5qE) p5.l0).LB) {
                ((X.5qE) p5.l0).L();
                return;
            } else {
                return;
            }
        } else {
            X.5qE v5_2 = ((X.5qE) p5.l0);
            if (v5_2.L <= 3) {
                long v2 = 0;
                android.view.View v1_0 = v5_2.L;
                if (v1_0 == 1) {
                    v2 = 5000;
                } else {
                    if (v1_0 == 2) {
                        v2 = 10000;
                    } else {
                        if (v1_0 == 3) {
                            v2 = 30000;
                        }
                    }
                }
                v5_2.L = (v5_2.L + 1);
                com.bytedance.bpea.transmit.hook.HandlerHook.viewPostDelay(v5_2.LCC, v5_2.LC, v2);
                v5_2.LC();
            }
            return;
        }
    }


}