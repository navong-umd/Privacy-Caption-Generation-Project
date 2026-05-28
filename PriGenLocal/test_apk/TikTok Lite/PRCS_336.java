/*Application Package Name: com.tiktok.lite.go
class PRCS_336 {
/**
X.0Ic;L(Landroid/content/Context;)V
*/

    public final declared_synchronized void L(android.content.Context p25)
    {
        try {
            this.LC = p25;
        } catch (int v1_8) {
            throw v1_8;
        }
        if ((!X.0Ic.LBL()) || (this.LBL)) {
            return;
        } else {
            android.net.ConnectivityManager v11_1 = ((android.net.ConnectivityManager) X.2Lr.LCC().LB.getSystemService("connectivity"));
            if (v11_1 != null) {
                android.net.NetworkRequest v4_0 = new android.net.NetworkRequest$Builder().addTransportType(0).addTransportType(1).addCapability(12);
                if (android.os.Build$VERSION.SDK_INT >= 28) {
                    v4_0.addCapability(21);
                }
                if (android.os.Build$VERSION.SDK_INT >= 23) {
                    v4_0.addCapability(16);
                }
                android.net.NetworkRequest v4_1 = v4_0.build();
                X.0Ib v3_4 = new X.0Ib(this, 0);
                com.bytedance.helios.statichook.api.HeliosApiHook v6_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                Object[] v12 = new Object[2];
                v12[0] = v4_1;
                v12[1] = v3_4;
                com.bytedance.helios.statichook.api.ExtraInfo v13_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/NetworkRequest;Landroid/net/ConnectivityManager$NetworkCallback;)V", "dzBzEgAjS8/YVFkiQFyFaHCZkp+e+KI3kePSCIlq6CHqIYXJ2F/FTdUFhesRGBY8fpV7+Grf");
                if (!v6_1.preInvoke(85, "android/net/ConnectivityManager", "registerNetworkCallback", v11_1, v12, "void", v13_1).intercept) {
                    v11_1.registerNetworkCallback(v4_1, v3_4);
                    v6_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v11_1, v12, v13_1, 1);
                    this.LBL = 1;
                    return;
                } else {
                    v6_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v11_1, v12, v13_1, 0);
                    this.LBL = 1;
                    return;
                }
            } else {
                X.2Lr.LCC().LBL.L = 0;
                return;
            }
        }
    }

/**
X.4ak;L()LX/1nY;
*/

    public final X.1nY L()
    {
        X.2Lr v7 = X.2Lr.LCC();
        if (!v7.LB()) {
            this.getClass();
            try {
                if (!v7.LB()) {
                    X.0IO v3_1 = new X.0IO(X.16B.LB, 0);
                    v3_1.L = X.4ak.LB();
                    v3_1.LB = X.4af.L;
                    v3_1.LC = new X.4ag();
                    X.0Io v4_1 = new X.0Io();
                    v4_1.L = 1;
                    v4_1.LB = new X.4ah();
                    X.0Ic v1_2 = new X.0Ir[1];
                    v1_2[0] = X.4ai.L;
                    v4_1.L(v1_2);
                    if (X.4a1.L()) {
                        X.0Ic v1_3 = new X.0Ir[1];
                        v1_3[0] = new X.4a4();
                        v4_1.L(v1_3);
                    }
                    X.2Lr v2_2 = new X.2Lt(v4_1, 0);
                    if (v3_1.LBL == null) {
                        v3_1.LBL = new java.util.HashMap();
                    }
                    v3_1.LBL.put(v2_2.LB(), v2_2);
                    if (!X.2Lr.LCC().LB()) {
                        X.2Lr.LCC().L(v3_1.LCC, v3_1.L);
                        X.2Lr.LCC().L(v3_1.LB);
                        X.2Lr.LCC().L(v3_1.LC);
                        X.2Lr.LCC();
                        X.2Lr.LCC().L();
                        X.2Lr v2_4 = v3_1.LBL.entrySet().iterator();
                        while (v2_4.hasNext()) {
                            X.2Lr.LCC().L(((X.1na) ((java.util.Map$Entry) v2_4.next()).getValue()));
                        }
                        X.0Ic.L.L(v3_1.LCC.getApplicationContext());
                        X.2Lr.LCC().LC();
                    }
                    com.bytedance.ies.abmock.SettingsManager.L().L(new X.4aj(X.2Lr.LCC()));
                }
            } catch (X.2Lr v0_3) {
                throw v0_3;
            }
        }
        return v7;
    }

/**
Y.ARunnableS4S0100000_2;run$53(LY/ARunnableS4S0100000_2;)V
*/

    public static final void run$53(Y.ARunnableS4S0100000_2 p1)
    {
        java.util.concurrent.ExecutorService v1_2 = ((X.6uW) p1.l0);
        if (!v1_2.LIIIJJLL) {
            v1_2.LIIIJJLL = 1;
            if (!X.4a0.LBL) {
                X.4ak.LB.L();
            } else {
                X.4TM.LBL().execute(X.5e9.L);
                return;
            }
        }
        return;
    }


}