/*Application Package Name: com.tiktok.lite.go
class PRCS_332 {
/**
com.ss.android.ugc.aweme.utils.NetworkObserverServiceImpl;L(LX/5qS;)V
*/

    public final void L(X.5qS p23)
    {
        if (!X.76e.LCCII) {
            try {
                if (!X.76T.L()) {
                    X.76e.LBL.start();
                    X.76e.LC = new X.7oe(X.76e.LBL.getLooper());
                }
            } catch (Throwable v0_16) {
                v0_16.printStackTrace();
            }
            X.76e.LCC = new X.76b();
            android.net.ConnectivityManager$NetworkCallback v2_1 = new android.net.NetworkRequest$Builder();
            v2_1.addCapability(12);
            android.net.ConnectivityManager v10_0 = X.16B.LB.getSystemService("connectivity");
            if (v10_0 == null) {
                throw new NullPointerException("null cannot be cast to non-null type android.net.ConnectivityManager");
            } else {
                android.net.ConnectivityManager v10_1 = ((android.net.ConnectivityManager) v10_0);
                X.76e.LB = v10_1;
                if (v10_1 != null) {
                    android.net.NetworkRequest v3 = v2_1.build();
                    android.net.ConnectivityManager$NetworkCallback v2_2 = X.76e.LCC;
                    com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                    Object[] v11 = new Object[2];
                    v11[0] = v3;
                    v11[1] = v2_2;
                    com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/NetworkRequest;Landroid/net/ConnectivityManager$NetworkCallback;)V", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KP+8apPdkhyC+vMYsNtSxePEdc9mI+KhjH9gog==");
                    if (!v5_1.preInvoke(85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, "void", v12_1).intercept) {
                        v10_1.registerNetworkCallback(v3, v2_2);
                        v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, v12_1, 1);
                    } else {
                        v5_1.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, v12_1, 0);
                    }
                }
                X.76e.LCCII = 1;
            }
        }
        if (p23.L == null) {
            return;
        } else {
            try {
                X.76e.L.add(p23);
                return;
            } catch (Throwable v0_19) {
                throw v0_19;
            }
        }
    }


}