/*Application Package Name: com.tiktok.lite.go
class PRCS_334 {
/**
X.5R6;L(Ljava/lang/Integer;)V
*/

    public final void L(Integer p24)
    {
        try {
            if (X.7Fg.L == null) {
                boolean v0_24;
                X.7Fg.L = new X.6Mc();
                X.7Fe.LC = 0;
                android.net.NetworkRequest v3_4 = X.7FY.LB();
                if (v3_4 != X.7Fe.L().getLong("last_record_date", 0)) {
                    v0_24 = 0;
                } else {
                    v0_24 = 1;
                }
                boolean v0_31;
                if (!v0_24) {
                    v0_31 = 1;
                } else {
                    v0_31 = (X.7Fe.L().getInt("cold_boot_times", 0) + 1);
                }
                X.7Fe.LB = v0_31;
                X.7Gj v2_6 = X.7Fe.L();
                v2_6.storeLong("last_record_date", v3_4);
                v2_6.storeInt("cold_boot_times", X.7Fe.LB);
                String v4_3 = new org.json.JSONObject();
                android.net.NetworkRequest v3_1 = 0;
                try {
                    boolean v0_37 = ((X.7rA) X.7Fg.L(0));
                } catch (org.json.JSONException) {
                    com.ss.android.ugc.aweme.incentive.service.LiteMonitorService.L().L("touchpoint_initialize_monitor", v4_3);
                    android.net.NetworkRequest v3_3 = new java.util.HashMap();
                    v3_3.put(Integer.valueOf(0), new X.6iw());
                    v3_3.put(Integer.valueOf(1), new X.6j3());
                    v3_3.put(Integer.valueOf(4), new X.6iy());
                    v3_3.put(Integer.valueOf(6), new X.6j1());
                    v3_3.put(Integer.valueOf(23), new X.6j2());
                    v3_3.put(Integer.valueOf(11), new X.6j4());
                    v3_3.put(Integer.valueOf(8), new X.6iz());
                    v3_3.put(Integer.valueOf(13), new X.6j0());
                    v3_3.put(Integer.valueOf(29), new X.6iv());
                    v3_3.put(Integer.valueOf(32), new X.6iu());
                    v3_3.put(Integer.valueOf(1003), new X.6ix());
                    X.7Fg.LB = v3_3;
                    boolean v0_11 = ((X.7rA) X.7Fg.L(0));
                    if (v0_11) {
                        String v4_0 = v0_11.LB();
                        if (v4_0 != null) {
                            android.net.ConnectivityManager v10_0 = v4_0.getSystemService("connectivity");
                            if ((v10_0 instanceof android.net.ConnectivityManager)) {
                                android.net.ConnectivityManager v10_1 = ((android.net.ConnectivityManager) v10_0);
                                if (v10_1 != null) {
                                    X.7Gk.L = X.7Gk.L(v4_0);
                                    android.net.NetworkRequest v3_0 = new android.net.NetworkRequest$Builder().addCapability(12).addTransportType(1).addTransportType(0).build();
                                    X.7Gj v2_5 = new X.7Gj(v4_0);
                                    com.bytedance.helios.statichook.api.HeliosApiHook v5_2 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                    Object[] v11 = new Object[2];
                                    v11[0] = v3_0;
                                    v11[1] = v2_5;
                                    com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/NetworkRequest;Landroid/net/ConnectivityManager$NetworkCallback;)V", "dzBzEhEpEcvSUUUuTBbKc9NnF3E3f2I9cuO+ZtHK3SZlA45xXxehMNG7TjUmcKElHsEi3zF+kRQ=");
                                    if (!v5_2.preInvoke(85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, "void", v12_1).intercept) {
                                        v10_1.registerNetworkCallback(v3_0, v2_5);
                                        v5_2.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, v12_1, 1);
                                    } else {
                                        v5_2.postInvoke(0, 85, "android/net/ConnectivityManager", "registerNetworkCallback", v10_1, v11, v12_1, 0);
                                    }
                                }
                            }
                        }
                    }
                }
                if (v0_37) {
                    v3_1 = v0_37.L();
                }
                v4_3.put("region", v3_1);
            }
        } catch (Throwable) {
        }
        Integer v1_1 = X.3tJ.LC();
        if ((v1_1 == null) || ((v1_1.length() == 0) || ("0".equals(v1_1)))) {
            X.3tJ.L(this.L);
        } else {
            com.ss.android.ugc.aweme.incentive.LiteTouchPointsManager.LC().L(p24);
        }
        X.7Fg.L(0);
        return;
    }

/**
Y.ARunnableS1S0000000_2;run$0(LY/ARunnableS1S0000000_2;)V
*/

    public static final void run$0(Y.ARunnableS1S0000000_2 p2)
    {
        X.5R0.L().L(Integer.valueOf(1));
        com.ss.android.ugc.aweme.incentive.IncentiveServiceImpl.LB = 1;
        return;
    }

/**
Y.ARunnableS1S0000000_2;run()V
*/

    public final void run()
    {
        switch (this.$t) {
            case 0:
                Y.ARunnableS1S0000000_2.run$0(this);
                return;
            case 1:
                Y.ARunnableS1S0000000_2.run$1(this);
                return;
            case 2:
                Y.ARunnableS1S0000000_2.run$2(this);
                return;
            case 3:
                Y.ARunnableS1S0000000_2.run$3(this);
                return;
            case 4:
                Y.ARunnableS1S0000000_2.run$4(this);
                return;
            case 5:
                Y.ARunnableS1S0000000_2.run$5(this);
                return;
            case 6:
                Y.ARunnableS1S0000000_2.run$6(this);
                return;
            case 7:
                Y.ARunnableS1S0000000_2.run$7(this);
                return;
            case 8:
                Y.ARunnableS1S0000000_2.run$8(this);
                return;
            case 9:
                Y.ARunnableS1S0000000_2.run$9(this);
                return;
            case 10:
                Y.ARunnableS1S0000000_2.run$10(this);
                return;
            case 11:
                Y.ARunnableS1S0000000_2.run$11(this);
                return;
            case 12:
                Y.ARunnableS1S0000000_2.run$12(this);
                return;
            default:
                return;
        }
    }


}