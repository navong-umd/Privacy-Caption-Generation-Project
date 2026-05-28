/*Application Package Name: com.tiktok.lite.go
class PRCS_53 {
/**
com.ss.android.ugc.aweme.recommend.FeaturesUtils;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPitYJDD0TeVAOf1kzTOlljWL11fQB7S");
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
com.ss.android.ugc.aweme.recommend.FeaturesUtils;L(Landroid/content/Context;)I
*/

    public static int L(android.content.Context p21)
    {
        try {
            Integer v5_4 = p21.getSystemService("connectivity");
        } catch (Exception) {
            return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.UNKNOWN.ordinal();
        }
        if (v5_4 == null) {
            throw new NullPointerException("null cannot be cast to non-null type android.net.ConnectivityManager");
        } else {
            Integer v5_1 = ((android.net.ConnectivityManager) v5_4);
            android.net.NetworkInfo v9;
            System.nanoTime();
            if (X.5uK.LB().L) {
                if ((X.75K.L()) || (X.5uK.LB().LB)) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = com.ss.android.ugc.aweme.recommend.FeaturesUtils.L(v5_1);
                            v9 = X.5uC.L;
                            if ((v9 == null) || (!v9.isAvailable())) {
                                return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.UNKNOWN.ordinal();
                            } else {
                                String v3_0;
                                com.bytedance.helios.statichook.api.HeliosApiHook v4_4 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                Object[] v10_1 = new Object[0];
                                com.bytedance.helios.statichook.api.ExtraInfo v11_3 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPitYJDD0TeVAOf1kzTOlljWL11fQB7S");
                                String v3_3 = v4_4.preInvoke(10216, "android/net/NetworkInfo", "getType", v9, v10_1, "int", v11_3);
                                if (!v3_3.intercept) {
                                    v3_0 = v9.getType();
                                    v4_4.postInvoke(Integer.valueOf(v3_0), 10216, "android/net/NetworkInfo", "getType", v9, v10_1, v11_3, 1);
                                } else {
                                    v4_4.postInvoke(0, 10216, "android/net/NetworkInfo", "getType", v9, v10_1, v11_3, 0);
                                    v3_0 = ((Integer) v3_3.returnValue).intValue();
                                }
                                if (1 != v3_0) {
                                    if (v3_0 != null) {
                                        return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.UNKNOWN.ordinal();
                                    } else {
                                        int v1_2;
                                        com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                        Object[] v10_0 = new Object[0];
                                        com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPitYJDD0TeVAOf1kzTOlljWL11fQB7S");
                                        int v1_1 = v4_1.preInvoke(10214, "android/net/NetworkInfo", "getSubtype", v9, v10_0, "int", v11_1);
                                        if (!v1_1.intercept) {
                                            v1_2 = v9.getSubtype();
                                            v4_1.postInvoke(Integer.valueOf(v1_2), 10214, "android/net/NetworkInfo", "getSubtype", v9, v10_0, v11_1, 1);
                                        } else {
                                            v4_1.postInvoke(0, 10214, "android/net/NetworkInfo", "getSubtype", v9, v10_0, v11_1, 0);
                                            v1_2 = ((Integer) v1_1.returnValue).intValue();
                                        }
                                        if (v1_2 != 3) {
                                            if (v1_2 == 20) {
                                                return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.MOBILE_5G.ordinal();
                                            } else {
                                                if ((v1_2 != 5) && (v1_2 != 6)) {
                                                    switch (v1_2) {
                                                        case 8:
                                                        case 9:
                                                        case 10:
                                                        case 8:
                                                        case 9:
                                                        case 10:
                                                            break;
                                                        case 8:
                                                        case 9:
                                                        case 10:
                                                            break;
                                                        default:
                                                            switch (v1_2) {
                                                                case 12:
                                                                case 14:
                                                                case 15:
                                                                    break;
                                                                case 13:
                                                                    return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.MOBILE_4G.ordinal();
                                                                case 12:
                                                                case 14:
                                                                case 15:
                                                                    break;
                                                                case 12:
                                                                case 14:
                                                                case 15:
                                                                    break;
                                                                default:
                                                                    return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.MOBILE_2G.ordinal();
                                                            }
                                                    }
                                                }
                                            }
                                        }
                                        return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.MOBILE_3G.ordinal();
                                    }
                                } else {
                                    return com.ss.android.ugc.aweme.recommend.FeaturesUtils$NetworkType.WIFI.ordinal();
                                }
                            }
                        } else {
                            if (X.5uO.L) {
                                X.5uQ.L("cm_net_info", com.ss.android.ugc.aweme.recommend.FeaturesUtils.L(v5_1).toString(), X.5uC.L.toString());
                            }
                            v9 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v9 = com.ss.android.ugc.aweme.recommend.FeaturesUtils.L(v5_1);
                    }
                } else {
                    v9 = com.ss.android.ugc.aweme.recommend.FeaturesUtils.L(v5_1);
                }
            } else {
                v9 = com.ss.android.ugc.aweme.recommend.FeaturesUtils.L(v5_1);
            }
        }
    }

/**
X.5HP;L(Z)LX/5HX;
*/

    public static X.5HX L(boolean p14)
    {
        try {
            float v0_35;
            System.currentTimeMillis();
            X.5HP.LCC = com.ss.android.ugc.aweme.HomePageServiceImpl.LB(0).LIILLL();
            X.5HP.LCCII = com.ss.android.ugc.aweme.recommend.FeaturesUtils.L(X.16B.LB);
            X.5HP.LCI = X.16B.LB.getResources().getConfiguration().fontScale;
            X.5HP.LD = X.5nq.L;
            X.5HP.LF = X.5nq.LB;
            X.5HP.LFF = ((((float) (Runtime.getRuntime().maxMemory() - (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()))) / 1149239296) / 1149239296);
            float v1_4 = -1082130432;
        } catch (Exception) {
            return X.5HP.LI;
        }
        if (!X.5nf.L()) {
            v0_35 = -1082130432;
        } else {
            if (!com.ss.android.ugc.aweme.recommend.FeaturesUtils.L) {
                com.ss.android.ugc.aweme.recommend.FeaturesUtils.L().LB();
                com.ss.android.ugc.aweme.recommend.FeaturesUtils.L = 1;
            }
            com.ss.android.ugc.aweme.recommend.FeaturesUtils.L().LCCII();
            v0_35 = (((float) X.7xA.L((((float) com.ss.android.ugc.aweme.recommend.FeaturesUtils.L().LCI()) * 1148846080))) / 1148846080);
        }
        float v0_47;
        X.5HP.LFFFF = v0_35;
        if (!X.5nf.L()) {
            v0_47 = -1082130432;
        } else {
            if (!com.ss.android.ugc.aweme.recommend.FeaturesUtils.L) {
                com.ss.android.ugc.aweme.recommend.FeaturesUtils.L().LB();
                com.ss.android.ugc.aweme.recommend.FeaturesUtils.L = 1;
            }
            com.ss.android.ugc.aweme.recommend.FeaturesUtils.L().LCCII();
            v0_47 = com.ss.android.ugc.aweme.recommend.FeaturesUtils.L().LCC();
        }
        X.5HP.LFFL = v0_47;
        float v4_2 = X.16G.LI.L();
        if (v4_2 != 0) {
            if (!X.5th.L()) {
                throw new X.5tf();
            } else {
                int v3_0 = v4_2.getResources().getInteger(v4_2.getResources().getIdentifier("config_screenBrightnessSettingMaximum", "integer", "android"));
                float v1_2 = android.provider.Settings$System.getInt(v4_2.getContentResolver(), "screen_brightness");
                if ((v3_0 == -1) || (v1_2 == -1)) {
                    throw new X.5tf();
                } else {
                    X.5tg v2_1 = new X.5tg(v3_0, v1_2);
                    v1_4 = (((float) v2_1.LB) / ((float) v2_1.L));
                }
            }
        }
        X.5HP.LFFLLL = v1_4;
        X.5HP.LC = X.669.L();
        X.5tg v2_2 = X.5HP.LBL;
        float v0_17 = X.5HP.LB;
        if (v2_2.size() > v0_17) {
            float v1_7 = (v2_2.size() - 1);
            v2_2 = v2_2.subList((v1_7 - v0_17), v1_7);
        }
        float v1_9;
        X.5tg v2_4 = new X.5HY(new X.5Hf(X.5HP.LD, X.5HP.LF, X.5HP.LFF, X.5HP.LFFFF, X.5HP.LFFL, X.5HP.LCC, X.5HP.LCCII, X.5HP.LCI, X.5HP.LFFLLL, X.5HP.LC), new X.5He(v2_2, X.5HP.LBL()));
        X.5HS.L.clear();
        if (!p14) {
            v1_9 = 0;
        } else {
            v1_9 = X.5GF.LB();
        }
        return new X.5HX(v2_4, v1_9);
    }


}