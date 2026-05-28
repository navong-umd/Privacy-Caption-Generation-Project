/*Application Package Name: com.tiktok.lite.go
class PRCS_28 {
/**
X.37B;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGNXrhfGIkHC6cR027Knu/N9uMJUfBhx/JzuZQs1Eex4CJMXwImsOzK8w=");
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
X.37B;LB(LX/37B; LX/35L; I Ljava/lang/Runnable;)V
*/

    public static synthetic void LB(X.37B p11, X.35L p12, int p13, Runnable p14)
    {
        try {
            String v3_0 = p11.LCCII;
            X.35R v1_14 = p11.LBL;
            java.util.Objects.requireNonNull(v1_14);
            v3_0.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$1(v1_14));
            java.util.HashMap v4_3 = ((android.net.ConnectivityManager) p11.L.getSystemService("connectivity"));
        } catch (Integer v0_54) {
            p14.run();
            throw v0_54;
        }
        Integer v0_62;
        System.nanoTime();
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.37B.L(v4_3);
                        v0_62 = X.5uC.L;
                        if ((v0_62 == null) || (!v0_62.isConnected())) {
                            p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$4(p11, p12, p13));
                        } else {
                            String v3_2 = p11.LB.L(p12.L());
                            X.352.L(0);
                            long v11_1 = 0;
                            while (((Boolean) p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$7(p11, p12))).booleanValue()) {
                                Iterable v9_1 = ((Iterable) p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$1(p11, p12)));
                                if (v9_1.iterator().hasNext()) {
                                    java.util.HashMap v4_4;
                                    if (v3_2 != null) {
                                        java.util.HashMap v4_1 = new java.util.ArrayList();
                                        X.35R v1_0 = v9_1.iterator();
                                        while (v1_0.hasNext()) {
                                            v4_1.add(((X.36R) v1_0.next()).LBL());
                                        }
                                        if (p12.LC()) {
                                            java.util.Iterator v5_0 = p11.LCCII;
                                            X.35R v1_1 = p11.LF;
                                            java.util.Objects.requireNonNull(v1_1);
                                            X.34j v6_1 = ((X.34j) v5_0.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$2(v1_1)));
                                            java.util.Iterator v5_1 = X.34w.LF();
                                            v5_1.L(p11.LCI.L());
                                            v5_1.LB(p11.LD.L());
                                            v5_1.L("GDT_CLIENT_METRICS");
                                            v5_1.L(new X.35c(new X.33X("proto"), X.35f.L.L(v6_1)));
                                            v4_1.add(v3_2.L(v5_1.LB()));
                                        }
                                        X.35R v1_4 = new X.34z();
                                        v1_4.L(v4_1);
                                        v1_4.L(p12.LB());
                                        v4_4 = v3_2.L(v1_4.L());
                                    } else {
                                        X.35F.L("Uploader");
                                        v4_4 = X.352.LC();
                                    }
                                    if (v4_4.L() != X.357.TRANSIENT_ERROR) {
                                        p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$3(p11, v9_1));
                                        if (v4_4.L() != X.357.OK) {
                                            if (v4_4.L() == X.357.INVALID_PAYLOAD) {
                                                java.util.HashMap v4_6 = new java.util.HashMap();
                                                java.util.Iterator v5_2 = v9_1.iterator();
                                                while (v5_2.hasNext()) {
                                                    X.35R v1_10 = ((X.36R) v5_2.next()).LBL().L();
                                                    if (v4_6.containsKey(v1_10)) {
                                                        v4_6.put(v1_10, Integer.valueOf((((Integer) v4_6.get(v1_10)).intValue() + 1)));
                                                    } else {
                                                        v4_6.put(v1_10, Integer.valueOf(1));
                                                    }
                                                }
                                                p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$9(p11, v4_6));
                                            }
                                        } else {
                                            v11_1 = Math.max(v11_1, v4_4.LB());
                                            if (p12.LC()) {
                                                p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$2(p11));
                                            }
                                        }
                                    } else {
                                        p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$6(p11, v9_1, p12, v11_1));
                                        p11.LC.L(p12, (p13 + 1), 1);
                                    }
                                }
                            }
                            p11.LCCII.L(new com.google.android.datatransport.runtime.scheduling.jobscheduling.-$$Lambda$e$5(p11, p12, v11_1));
                        }
                        p14.run();
                        return;
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", X.37B.L(v4_3).toString(), X.5uC.L.toString());
                        }
                        v0_62 = X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    v0_62 = X.37B.L(v4_3);
                }
            } else {
                v0_62 = X.37B.L(v4_3);
            }
        } else {
            v0_62 = X.37B.L(v4_3);
        }
    }

/**
com.google.android.datatransport.runtime.scheduling.jobscheduling.-;run()V
*/

    public final void run()
    {
        X.37B.LB(this.f$0, this.f$1, this.f$2, this.f$3);
        return;
    }


}